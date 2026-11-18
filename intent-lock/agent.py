"""A small deterministic calendar agent using only Intent Lock's HTTP tools.

Approve a permission in the UI, then run: python agent.py
The agent never has direct access to the calendar store.
"""
import json
import argparse
from datetime import date, datetime, time, timedelta
from urllib.request import Request, urlopen

BASE = 'http://127.0.0.1:8000/api/'

def call(path, payload=None):
    request = Request(BASE + path, data=None if payload is None else json.dumps(payload).encode(), headers={'Content-Type':'application/json'})
    with urlopen(request) as response:
        return json.load(response)

def try_action(action):
    result = call('action', action)
    print(json.dumps({'tool':'calendar_action','input':action,'result':result}))
    return result

def main():
    policy = call('state')['policy']
    if not policy or policy['used']:
        print('Approve a fresh permission in the UI first.')
        return
    mid = policy['meeting_id']
    if policy.get('type') == 'add_attendee':
        try_action({'type':'cancel','meeting_id':mid})
        try_action({'type':'add_attendee','meeting_id':mid,'attendee':policy['attendee'] + ' (unapproved)'})
        try_action({'type':'add_attendee','meeting_id':mid,'attendee':policy['attendee']})
        return
    try_action({'type':'add_attendee','meeting_id':mid,'attendee':'Mallory'})
    start, end = date.fromisoformat(policy['start_date']), date.fromisoformat(policy['end_date'])
    day = start
    while day <= end:
        if day.weekday() not in policy['days']:
            try_action({'type':'reschedule','meeting_id':mid,'date':day.isoformat(),'time':policy['earliest']})
            break
        day += timedelta(days=1)
    day = start
    while day <= end:
        if day.weekday() in policy['days']:
            hour, minute = map(int, policy['earliest'].split(':'))
            last_h, last_m = map(int, policy['latest'].split(':'))
            for mins in range(hour*60+minute,last_h*60+last_m+1,30):
                if datetime.combine(day, time(mins//60, mins%60)) <= datetime.now(): continue
                result = try_action({'type':'reschedule','meeting_id':mid,'date':day.isoformat(),'time':f'{mins//60:02}:{mins%60:02}'})
                if result['allowed']: return
                if 'conflicts' not in result['reason']: return
        day += timedelta(days=1)
    print('No available slot found within the approved boundaries.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Intent Lock demo agent')
    parser.add_argument('--port', type=int, default=8000)
    args = parser.parse_args()
    BASE = f'http://127.0.0.1:{args.port}/api/'
    main()
