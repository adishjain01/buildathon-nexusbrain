import json
import argparse
import socket
import os
import re
import threading
import uuid
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import openrouter_agent
import chat_tasks

ROOT = Path(__file__).parent
lock = threading.RLock()
state = {}
session_key = ''

def openrouter_key():
    if session_key:
        return session_key
    key = os.environ.get('OPENROUTER_API_KEY', '').strip()
    path = ROOT / '.env'
    if not key and path.is_file():
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            name, separator, value = line.partition('=')
            if separator and name.strip() == 'OPENROUTER_API_KEY':
                key = value.strip().strip('"\'')
                break
    return key

class DemoServer(ThreadingHTTPServer):
    def server_bind(self):
        # Windows SO_REUSEADDR allows competing listeners on the same port.
        # Exclusive binding fails clearly instead of routing requests unpredictably.
        if hasattr(socket, 'SO_EXCLUSIVEADDRUSE'):
            self.allow_reuse_address = False
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()

def reset():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    state.clear()
    state.update(meetings=[
        {'id':'m1','title':'Project sync','attendees':['you','Priya'],'date':(monday+timedelta(days=2)).isoformat(),'time':'10:00','duration':30,'version':1},
        {'id':'m2','title':'Design review','attendees':['you','Alex'],'date':(monday+timedelta(days=3)).isoformat(),'time':'15:00','duration':30,'version':1},
        {'id':'m3','title':'Team standup','attendees':['you','Sam'],'date':(monday+timedelta(days=4)).isoformat(),'time':'11:00','duration':30,'version':1}], policy=None, audit=[])

def audit(action, allowed, reason):
    state['audit'].insert(0, {'action': action, 'allowed': allowed, 'reason': reason, 'at':datetime.now().strftime('%H:%M:%S')})
    return {'allowed':allowed, 'reason':reason}

def valid_time(value):
    try:
        return isinstance(value, str) and datetime.strptime(value, '%H:%M').strftime('%H:%M') == value
    except ValueError:
        return False

def approve(body, preview=False):
    meeting = next((m for m in state['meetings'] if m['id'] == body.get('meeting_id')), None)
    if not meeting: raise ValueError('Choose an existing meeting.')
    if 'meeting_version' in body and body['meeting_version'] != meeting['version']:
        raise ValueError('The meeting changed since review. Submit your task again.')
    kind = body.get('type', 'reschedule')
    if kind == 'add_attendee':
        attendee = body.get('attendee')
        if not isinstance(attendee, str) or not attendee.strip() or len(attendee.strip()) > 100 or any(ord(c) < 32 for c in attendee):
            raise ValueError('Enter a valid attendee name or email (up to 100 characters).')
        attendee = attendee.strip()
        if attendee.casefold() in (x.casefold() for x in meeting['attendees']):
            raise ValueError('This attendee is already on the meeting.')
        policy = {'id':str(uuid.uuid4()), 'type':kind, 'meeting_id':meeting['id'], 'meeting_version':meeting['version'], 'attendee':attendee, 'expires_at':(datetime.now()+timedelta(minutes=15)).isoformat(), 'used':False}
        if not preview: state['policy'] = policy
        return policy
    if kind != 'reschedule': raise ValueError('Unsupported permission type.')
    try:
        start, end = date.fromisoformat(body['start_date']), date.fromisoformat(body['end_date'])
        days = body['days']
        if start > end or (end - start).days > 31 or not isinstance(days, list) or not days or any(type(d) is not int or d not in range(7) for d in days): raise ValueError()
        if not valid_time(body['earliest']) or not valid_time(body['latest']) or body['earliest'] > body['latest']: raise ValueError()
    except (KeyError, TypeError, ValueError): raise ValueError('Enter a valid date range, time range, and at least one day.')
    # This demonstration uses server-local calendar time and a short-lived capability.
    policy = {'id':str(uuid.uuid4()), 'type':kind, 'meeting_id':meeting['id'], 'meeting_version':meeting['version'], 'start_date':start.isoformat(), 'end_date':end.isoformat(), 'earliest':body['earliest'], 'latest':body['latest'], 'days':sorted(set(days)), 'expires_at':(datetime.now()+timedelta(minutes=15)).isoformat(), 'used':False}
    if not preview: state['policy'] = policy
    return policy

def gateway(action):
    p = state['policy']
    if not isinstance(action, dict): return audit({}, False, 'Malformed action.')
    if not p: return audit(action, False, 'No active approved permission.')
    if p['used']: return audit(action, False, 'Permission already used.')
    if datetime.now() >= datetime.fromisoformat(p['expires_at']): return audit(action, False, 'Permission expired.')
    if action.get('type') != p['type']: return audit(action, False, 'This action type is not authorized by the permission.')
    if action.get('meeting_id') != p['meeting_id']: return audit(action, False, 'This is not the authorized meeting.')
    meeting = next((m for m in state['meetings'] if m['id'] == p['meeting_id']), None)
    if not meeting or meeting['version'] != p['meeting_version']: return audit(action, False, 'Meeting changed since approval; approve again.')
    if p['type'] == 'add_attendee':
        if set(action) != {'type','meeting_id','attendee'}: return audit(action, False, 'Only the approved attendee may be added.')
        if action.get('attendee') != p['attendee']: return audit(action, False, 'This attendee is not authorized.')
        if p['attendee'].casefold() in (x.casefold() for x in meeting['attendees']): return audit(action, False, 'Attendee is already on the meeting.')
        meeting['attendees'].append(p['attendee'])
        meeting['version'] += 1
        p['used'] = True
        return audit(action, True, 'Approved attendee added. Meeting time and other details were preserved.')
    if set(action) != {'type','meeting_id','date','time'}: return audit(action, False, 'Only the date and time may be changed.')
    try:
        day = date.fromisoformat(action['date'])
        if not valid_time(action['time']): raise ValueError()
    except (ValueError, TypeError, KeyError): return audit(action, False, 'Invalid date or time.')
    if not p['start_date'] <= day.isoformat() <= p['end_date']: return audit(action, False, 'Date is outside the approved range.')
    if day.weekday() not in p['days']: return audit(action, False, 'That day of the week is not approved.')
    if not p['earliest'] <= action['time'] <= p['latest']: return audit(action, False, 'Time is outside the approved window.')
    start = datetime.combine(day, datetime.strptime(action['time'], '%H:%M').time())
    if start <= datetime.now(): return audit(action, False, 'The proposed time is in the past.')
    end = start + timedelta(minutes=meeting['duration'])
    for other in state['meetings']:
        if other['id'] == meeting['id']: continue
        other_start = datetime.fromisoformat(other['date'] + 'T' + other['time'])
        if start < other_start + timedelta(minutes=other['duration']) and end > other_start:
            return audit(action, False, 'The proposed slot conflicts with another meeting.')
    meeting.update(date=day.isoformat(), time=action['time'], version=meeting['version']+1)
    p['used'] = True
    return audit(action, True, 'Rescheduled. Attendees and meeting details were preserved.')

def agent(scenario='normal'):
    # A deterministic demo agent calls the exact same gateway as manual actions.
    p = state['policy']
    if not p: raise ValueError('Approve a permission first.')
    results = []
    if scenario not in ('normal','injection','conflict'): raise ValueError('Unknown scenario.')
    if scenario == 'injection':
        other = next((m for m in state['meetings'] if m['id'] != p['meeting_id']), None)
        if other: results.append(gateway({'type':'cancel','meeting_id':other['id']}))
    if scenario == 'conflict' and p['type'] == 'reschedule':
        other = next((m for m in state['meetings'] if m['id'] != p['meeting_id']), None)
        if other: results.append(gateway({'type':'reschedule','meeting_id':p['meeting_id'],'date':other['date'],'time':other['time']}))
    if p['type'] == 'add_attendee':
        results.append(gateway({'type':'cancel','meeting_id':p['meeting_id']}))
        results.append(gateway({'type':'add_attendee','meeting_id':p['meeting_id'],'attendee':p['attendee'] + ' (unapproved)'}))
        results.append(gateway({'type':'add_attendee','meeting_id':p['meeting_id'],'attendee':p['attendee']}))
        return results
    results.append(gateway({'type':'add_attendee','meeting_id':p['meeting_id'],'attendee':'Mallory'}))
    start, end = date.fromisoformat(p['start_date']), date.fromisoformat(p['end_date'])
    day = start
    while day <= end:
        if day.weekday() not in p['days']:
            results.append(gateway({'type':'reschedule','meeting_id':p['meeting_id'],'date':day.isoformat(),'time':p['earliest']}))
            break
        day += timedelta(days=1)
    day = start
    while day <= end:
        if day.weekday() in p['days']:
            t = datetime.strptime(p['earliest'], '%H:%M')
            last = datetime.strptime(p['latest'], '%H:%M')
            while t <= last:
                if datetime.combine(day, t.time()) <= datetime.now():
                    t += timedelta(minutes=30)
                    continue
                result = gateway({'type':'reschedule','meeting_id':p['meeting_id'],'date':day.isoformat(),'time':t.strftime('%H:%M')})
                results.append(result)
                if result['allowed'] or result['reason'] != 'The proposed slot conflicts with another meeting.': return results
                t += timedelta(minutes=30)
        day += timedelta(days=1)
    return results

class Handler(BaseHTTPRequestHandler):
    def send_json(self, value, status=200):
        data = json.dumps(value).encode()
        self.send_response(status); self.send_header('Content-Type','application/json'); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
    def do_GET(self):
        if urlparse(self.path).path == '/api/state':
            with lock: self.send_json({**state, 'openrouter_configured':bool(openrouter_key())})
        elif self.path in ('/', '/app.js', '/style.css'):
            name = 'index.html' if self.path == '/' else self.path[1:]
            data = (ROOT / 'static' / name).read_bytes()
            self.send_response(200); self.send_header('Content-Type', {'index.html':'text/html; charset=utf-8','app.js':'text/javascript; charset=utf-8','style.css':'text/css; charset=utf-8'}[name]); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
        else: self.send_error(404)
    def do_POST(self):
        try:
            global session_key
            origin = self.headers.get('Origin')
            if origin and origin != 'http://' + self.headers.get('Host', ''):
                return self.send_json({'error':'Cross-origin requests are not allowed.'}, 403)
            size = int(self.headers.get('Content-Length','0'))
            if size > 10000: raise ValueError('Request too large.')
            body = json.loads(self.rfile.read(size) or b'{}')
            if self.path == '/api/interpret':
                chat_tasks.require_reschedule_bounds(body.get('text'))
            if self.path == '/api/interpret' and body.get('mode') == 'openrouter':
                key = openrouter_key()
                if not key: raise ValueError('Add an OpenRouter key in Agent settings first.')
                text = body.get('text')
                if not isinstance(text, str) or not text.strip() or len(text) > 500: raise ValueError('Enter a task of up to 500 characters.')
                if re.search(r'\b(?:remove|delete|cancel)\b', text, re.IGNORECASE):
                    raise ValueError('Removing attendees and cancelling meetings are not supported. Ask for one supported action: reschedule a meeting or add an attendee.')
                with lock: meetings = json.loads(json.dumps(state['meetings']))
                try:
                    proposal = openrouter_agent.interpret(key, text, meetings, date.today().isoformat())
                    source = 'openrouter'
                except RuntimeError as exc:
                    try:
                        proposal = chat_tasks.parse_task(text, meetings)
                    except ValueError:
                        raise ValueError(str(exc) + ' The local interpreter could not understand this task; use one of the example phrases.') from exc
                    source = 'local_fallback'
                original = next((m for m in meetings if m['id'] == proposal.get('meeting_id')), None)
                if not original: raise ValueError('The model did not identify a valid meeting; please clarify.')
                proposal['meeting_version'] = original['version']
                with lock:
                    checked = approve(proposal, preview=True)
                return self.send_json({**{k:v for k,v in checked.items() if k not in ('id','expires_at','used')}, '_source':source})
            if self.path == '/api/key':
                if set(body) != {'key'} or not isinstance(body['key'], str) or len(body['key']) > 512 or any(ord(c) < 32 for c in body['key']):
                    raise ValueError('Enter a valid API key.')
                with lock:
                    session_key = body['key'].strip()
                    self.send_json({'configured':bool(openrouter_key()), 'session_key_set':bool(session_key)})
                return
            if self.path == '/api/agent' and body.get('mode') == 'openrouter':
                key = openrouter_key()
                if not key: raise ValueError('OpenRouter key not configured. Use scripted mode or add OPENROUTER_API_KEY to intent-lock/.env.')
                with lock:
                    policy = dict(state['policy']) if state['policy'] else None
                    meetings = json.loads(json.dumps(state['meetings']))
                if not policy or policy['used']: raise ValueError('Approve a fresh permission first.')
                def execute(action):
                    with lock:
                        if not state['policy'] or state['policy']['id'] != policy['id']:
                            return audit(action, False, 'Permission changed during this run; action rejected.')
                        return gateway(action)
                scenario = body.get('scenario', 'normal')
                if scenario not in ('normal','injection','conflict'): raise ValueError('Unknown scenario.')
                result = openrouter_agent.run(key, policy, meetings, execute, scenario=scenario)
                return self.send_json(result)
            with lock:
                if self.path == '/api/reset': reset(); result = {'ok':True}
                elif self.path == '/api/interpret': result = chat_tasks.parse_task(body.get('text'), state['meetings'])
                elif self.path == '/api/approve': result = approve(body)
                elif self.path == '/api/action': result = gateway(body)
                elif self.path == '/api/agent':
                    if body.get('mode', 'scripted') not in ('scripted', 'auto'): raise ValueError('Unsupported agent mode.')
                    result = agent(body.get('scenario','normal'))
                else: return self.send_error(404)
                self.send_json(result)
        except (ValueError, TypeError, json.JSONDecodeError) as e: self.send_json({'error':str(e)},400)
        except RuntimeError as e: self.send_json({'error':str(e)},502)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Intent Lock local demo')
    parser.add_argument('--port', type=int, default=8000, help='local port (default: 8000)')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('port must be between 1 and 65535')
    reset()
    try:
        httpd = DemoServer(('127.0.0.1', args.port), Handler)
    except OSError as exc:
        print(f'Could not start on port {args.port}: {exc}. Try --port 8001.', flush=True)
        raise SystemExit(1)
    print(f'Intent Lock running at http://127.0.0.1:{args.port}/', flush=True)
    print('Keep this window open; press Ctrl+C to stop.', flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped.', flush=True)
    finally:
        httpd.server_close()
