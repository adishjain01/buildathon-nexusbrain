"""Strict task parser for the chat demo. Unknown language fails closed."""
import re
from datetime import date, timedelta

DAYS=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']

def parse_task(text, meetings):
    if not isinstance(text,str) or len(text)>500: raise ValueError('Enter a short task.')
    text=text.strip().rstrip('.').lower()
    add=re.fullmatch(r'(?:please )?add ([a-z][a-z0-9._@+ -]{0,99}?) to (?:the |my )?(?:meeting|meet) with ([a-z][a-z -]*)',text)
    if add:
        attendee, person=add.groups()
        matches=[m for m in meetings if any(a.casefold()==person.casefold() for a in m['attendees'] if a!='you')]
        if len(matches)!=1: raise ValueError('Could not identify exactly one meeting. Try Priya, Alex, or Sam.')
        return {'type':'add_attendee','meeting_id':matches[0]['id'],'meeting_version':matches[0]['version'],'attendee':attendee.strip()}
    match=re.fullmatch(r'(?:please )?(?:reschedule|move) (?:the |my )?(?:meeting|meet) with ([a-z][a-z -]*?)(?: (this week))?(?: (?:only )?after (\d{1,2})(?::(\d{2}))?\s*(am|pm))?(?: (?:and )?never (?:on )?(monday|tuesday|wednesday|thursday|friday|saturday|sunday))?',text)
    if not match: raise ValueError('Try: “Reschedule the meeting with Priya this week after 2 PM and never Friday”. Only this supported wording is accepted; nothing is silently ignored.')
    person=match.group(1).strip()
    matches=[m for m in meetings if any(a.casefold()==person.casefold() for a in m['attendees'] if a!='you')]
    if len(matches)!=1: raise ValueError('Could not identify exactly one meeting with that person. Try Priya, Alex, or Sam.')
    now=date.today(); end=now+timedelta(days=6-now.weekday())
    earliest='09:00'
    if match.group(3):
        hour=int(match.group(3)); minute=int(match.group(4) or 0)
        if hour<1 or hour>12 or minute>59: raise ValueError('Enter a valid time, such as 2 PM.')
        minutes=(hour%12+(12 if match.group(5)=='pm' else 0))*60+minute+1
        if minutes>1439: raise ValueError('That time leaves no available start time.')
        earliest=f'{minutes//60:02}:{minutes%60:02}'
    days=list(range(7))
    if match.group(6): days.remove(DAYS.index(match.group(6)))
    return {'type':'reschedule','meeting_id':matches[0]['id'],'meeting_version':matches[0]['version'],'start_date':now.isoformat(),'end_date':end.isoformat(),'earliest':earliest,'latest':'23:59','days':days}
