import json
import threading
import uuid
from datetime import date, datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
lock = threading.RLock()
state = {}

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

def approve(body):
    meeting = next((m for m in state['meetings'] if m['id'] == body.get('meeting_id')), None)
    if not meeting: raise ValueError('Choose an existing meeting.')
    try:
        start, end = date.fromisoformat(body['start_date']), date.fromisoformat(body['end_date'])
        days = body['days']
        if start > end or (end - start).days > 31 or not isinstance(days, list) or not days or any(type(d) is not int or d not in range(7) for d in days): raise ValueError()
        if not valid_time(body['earliest']) or not valid_time(body['latest']) or body['earliest'] > body['latest']: raise ValueError()
    except (KeyError, TypeError, ValueError): raise ValueError('Enter a valid date range, time range, and at least one day.')
    # This demonstration uses server-local calendar time and a short-lived capability.
    policy = {'id':str(uuid.uuid4()), 'meeting_id':meeting['id'], 'meeting_version':meeting['version'], 'start_date':start.isoformat(), 'end_date':end.isoformat(), 'earliest':body['earliest'], 'latest':body['latest'], 'days':sorted(set(days)), 'expires_at':(datetime.now()+timedelta(minutes=15)).isoformat(), 'used':False}
    state['policy'] = policy
    return policy

def gateway(action):
    p = state['policy']
    if not isinstance(action, dict): return audit({}, False, 'Malformed action.')
    if not p: return audit(action, False, 'No active approved permission.')
    if p['used']: return audit(action, False, 'Permission already used.')
    if datetime.now() >= datetime.fromisoformat(p['expires_at']): return audit(action, False, 'Permission expired.')
    if action.get('type') != 'reschedule': return audit(action, False, 'Only rescheduling is authorized.')
    if set(action) != {'type','meeting_id','date','time'}: return audit(action, False, 'Only the date and time may be changed.')
    if action.get('meeting_id') != p['meeting_id']: return audit(action, False, 'This is not the authorized meeting.')
    meeting = next((m for m in state['meetings'] if m['id'] == p['meeting_id']), None)
    if not meeting or meeting['version'] != p['meeting_version']: return audit(action, False, 'Meeting changed since approval; approve again.')
    try:
        day = date.fromisoformat(action['date'])
        if not valid_time(action['time']): raise ValueError()
    except (ValueError, TypeError, KeyError): return audit(action, False, 'Invalid date or time.')
    if not p['start_date'] <= day.isoformat() <= p['end_date']: return audit(action, False, 'Date is outside the approved range.')
    if day.weekday() not in p['days']: return audit(action, False, 'That day of the week is not approved.')
    if not p['earliest'] <= action['time'] <= p['latest']: return audit(action, False, 'Time is outside the approved window.')
    start = datetime.combine(day, datetime.strptime(action['time'], '%H:%M').time())
    end = start + timedelta(minutes=meeting['duration'])
    for other in state['meetings']:
        if other['id'] == meeting['id']: continue
        other_start = datetime.fromisoformat(other['date'] + 'T' + other['time'])
        if start < other_start + timedelta(minutes=other['duration']) and end > other_start:
            return audit(action, False, 'The proposed slot conflicts with another meeting.')
    meeting.update(date=day.isoformat(), time=action['time'], version=meeting['version']+1)
    p['used'] = True
    return audit(action, True, 'Rescheduled. Attendees and meeting details were preserved.')

def agent():
    # A deterministic demo agent calls the exact same gateway as manual actions.
    p = state['policy']
    if not p: raise ValueError('Approve a permission first.')
    results = []
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
            with lock: self.send_json(state)
        elif self.path in ('/', '/app.js', '/style.css'):
            name = 'index.html' if self.path == '/' else self.path[1:]
            data = (ROOT / 'static' / name).read_bytes()
            self.send_response(200); self.send_header('Content-Type', {'index.html':'text/html; charset=utf-8','app.js':'text/javascript; charset=utf-8','style.css':'text/css; charset=utf-8'}[name]); self.send_header('Content-Length',str(len(data))); self.end_headers(); self.wfile.write(data)
        else: self.send_error(404)
    def do_POST(self):
        try:
            size = int(self.headers.get('Content-Length','0'))
            if size > 10000: raise ValueError('Request too large.')
            body = json.loads(self.rfile.read(size) or b'{}')
            with lock:
                if self.path == '/api/reset': reset(); result = {'ok':True}
                elif self.path == '/api/approve': result = approve(body)
                elif self.path == '/api/action': result = gateway(body)
                elif self.path == '/api/agent': result = agent()
                else: return self.send_error(404)
                self.send_json(result)
        except (ValueError, TypeError, json.JSONDecodeError) as e: self.send_json({'error':str(e)},400)

if __name__ == '__main__':
    reset()
    print('Intent Lock running at http://127.0.0.1:8000', flush=True)
    ThreadingHTTPServer(('127.0.0.1',8000), Handler).serve_forever()
