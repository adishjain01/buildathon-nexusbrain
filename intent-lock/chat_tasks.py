"""Strict local interpreter: exact destination required for every reschedule."""
import re
from datetime import date, datetime, timedelta

class NeedsClarification(ValueError):
    pass

DAYS=['monday','tuesday','wednesday','thursday','friday','saturday','sunday']

def require_reschedule_bounds(text):
    if not isinstance(text,str): raise ValueError('Enter a task.')
    if not re.search(r'\b(?:reschedule|move)\b',text,re.I): return
    if re.search(r'\b(?:previous|original|old)\s+(?:meeting|event|slot)\b', text, re.I):
        raise ValueError('This prototype moves one meeting with all its attendees. It cannot keep someone in a separate previous meeting or split the event; please clarify or submit one supported action.')
    has_date=bool(re.search(r'\b(?:today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b|\b\d{4}-\d{2}-\d{2}\b',text,re.I))
    time_pattern=r'(?:\d{1,2}(?::\d{2})?\s*(?:am|pm)|(?:[01]?\d|2[0-3]):[0-5]\d)\b'
    has_time=bool(re.search(r'\bat\s+'+time_pattern,text,re.I)) or (bool(re.search(r'(?<![\d:])'+time_pattern,text,re.I)) and not re.search(r'\b(?:after|before|between)\b',text,re.I))
    if not has_date and not has_time: raise NeedsClarification('What exact date and time should the meeting move to? For example: “tomorrow at 3 PM”. A week or a time window alone is not a specific slot.')
    if not has_date: raise NeedsClarification('What exact date should the meeting move to? Please provide a date or a day such as “tomorrow”.')
    if not has_time: raise NeedsClarification('What exact time should the meeting move to? Please provide a time such as “at 3 PM”.')

def parse_task(text, meetings):
    if not isinstance(text,str) or len(text)>500: raise ValueError('Enter a short task.')
    require_reschedule_bounds(text)
    text=text.strip().rstrip('.')
    add=re.fullmatch(r'(?:please )?add ([a-z][a-z0-9._@+ -]{0,99}?) to (?:the |my )?(?:meeting|meet) with ([a-z][a-z -]*)',text,re.I)
    if add:
        attendee, person=add.groups()
        matches=[m for m in meetings if any(a.casefold()==person.casefold() for a in m['attendees'] if a!='you')]
        if len(matches)!=1: raise ValueError('Could not identify exactly one meeting. Try Priya, Alex, or Sam.')
        return {'type':'add_attendee','meeting_id':matches[0]['id'],'meeting_version':matches[0]['version'],'attendee':attendee.strip()}
    if re.fullmatch(r'(?:please )?add\s+to\s+(?:the |my )?(?:meeting|meet) with [a-z][a-z -]*', text, re.I):
        raise NeedsClarification('Who should be added to the meeting?')
    if re.fullmatch(r'(?:please )?add\s+[a-z][a-z0-9._@+ -]{0,99}\s+to\s+(?:the |my )?(?:meeting|meet)', text, re.I):
        raise NeedsClarification('Which meeting should receive the attendee? For example, reply “with Priya”.')
    m=re.fullmatch(r'(?:please )?(?:reschedule|move) (?:the |my )?(?:meeting|meet) with ([a-z][a-z -]*?) (?:(?:on|to) )?(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{4}-\d{2}-\d{2}) (?:at )?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?',text,re.I)
    if not m: raise ValueError('Try: “Reschedule the meeting with Priya tomorrow at 3 PM”. Unsupported wording is not silently ignored.')
    person, day_text, hour_text, minute_text, meridiem=m.groups()
    day_text=day_text.lower()
    meridiem=meridiem.lower() if meridiem else None
    matches=[item for item in meetings if any(a.casefold()==person.casefold() for a in item['attendees'] if a!='you')]
    if len(matches)!=1: raise ValueError('Could not identify exactly one meeting with that person. Try Priya, Alex, or Sam.')
    now=date.today()
    if day_text=='today': day=now
    elif day_text=='tomorrow': day=now+timedelta(days=1)
    elif day_text in DAYS: day=now+timedelta(days=(DAYS.index(day_text)-now.weekday())%7)
    else:
        try: day=date.fromisoformat(day_text)
        except ValueError: raise ValueError('Enter a valid date in YYYY-MM-DD format.')
    hour=int(hour_text); minute=int(minute_text or 0)
    if minute>59 or (meridiem and (hour<1 or hour>12)) or (not meridiem and (minute_text is None or hour>23)):
        raise ValueError('Enter a valid time, such as 3 PM or 15:00.')
    if meridiem: hour=hour%12+(12 if meridiem=='pm' else 0)
    exact_time=f'{hour:02}:{minute:02}'
    if datetime.combine(day, datetime.strptime(exact_time,'%H:%M').time()) <= datetime.now(): raise ValueError('That date and time are in the past. Please choose a future slot.')
    return {'type':'reschedule','meeting_id':matches[0]['id'],'meeting_version':matches[0]['version'],'start_date':day.isoformat(),'end_date':day.isoformat(),'earliest':exact_time,'latest':exact_time,'days':[day.weekday()]}
