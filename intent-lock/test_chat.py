import unittest
import chat_tasks
import server

class ChatTaskTests(unittest.TestCase):
    def setUp(self): server.reset()
    def test_reschedule_task_and_constraints(self):
        p=chat_tasks.parse_task('Reschedule the meeting with Priya tomorrow at 4 PM',server.state['meetings'])
        self.assertEqual(p['meeting_id'],'m1')
        self.assertEqual(p['earliest'],'16:00')
        self.assertEqual(p['latest'],'16:00')
        self.assertEqual(p['start_date'],p['end_date'])
        self.assertEqual(len(p['days']),1)
        self.assertEqual(p['meeting_version'],1)
    def test_simple_task_and_add_attendee(self):
        self.assertEqual(chat_tasks.parse_task('reschedule the meet with priya tomorrow at 4 PM',server.state['meetings'])['meeting_id'],'m1')
        p=chat_tasks.parse_task('Add Taylor to the meeting with Priya',server.state['meetings'])
        self.assertEqual((p['type'],p['attendee']),('add_attendee','Taylor'))
        server.approve(p)
        self.assertTrue(server.gateway({'type':'add_attendee','meeting_id':'m1','attendee':'Taylor'})['allowed'])
    def test_iso_date_time_without_at_and_case_preservation(self):
        from datetime import date, timedelta
        destination=(date.today()+timedelta(days=2)).isoformat()
        for time in ('11 am', '11:00', 'at 11 AM'):
            p=chat_tasks.parse_task(f'Reschedule the meeting with Priya to {destination} {time}',server.state['meetings'])
            self.assertEqual((p['start_date'],p['earliest']), (destination,'11:00'))
        p=chat_tasks.parse_task('Add Taylor to the meeting with Priya',server.state['meetings'])
        self.assertEqual(p['attendee'],'Taylor')
    def test_previous_meeting_request_is_not_silently_dropped(self):
        from datetime import date, timedelta
        destination=(date.today()+timedelta(days=2)).isoformat()
        with self.assertRaisesRegex(ValueError,'cannot keep someone'):
            chat_tasks.parse_task(f'Reschedule the meeting with Priya to {destination} 11 am and keep Taylor in previous meeting',server.state['meetings'])
        self.assertIsNone(server.state['policy'])
    def test_missing_date_or_time_is_not_assumed(self):
        for text in ['Reschedule the meeting with Priya', 'Reschedule the meeting with Priya this week', 'Reschedule the meeting with Priya this week after 2 PM']:
            with self.assertRaisesRegex(ValueError, 'What exact (date|time)'):
                chat_tasks.parse_task(text,server.state['meetings'])
            self.assertIsNone(server.state['policy'])
    def test_missing_attendee_or_meeting_requests_clarification(self):
        for text in ['Add to the meeting with Priya', 'Add Taylor to the meeting']:
            with self.assertRaises(chat_tasks.NeedsClarification):
                chat_tasks.parse_task(text,server.state['meetings'])
    def test_unsupported_or_ambiguous_input_is_rejected(self):
        for text in ['reschedule the meeting with Priya and cancel Alex', 'reschedule the meeting with Priya after lunch', 'reschedule the meeting with someone else']:
            with self.assertRaises(ValueError): chat_tasks.parse_task(text,server.state['meetings'])
    def test_review_rejects_stale_meeting(self):
        p=chat_tasks.parse_task('reschedule the meeting with Priya tomorrow at 4 PM',server.state['meetings'])
        server.state['meetings'][0]['version']+=1
        with self.assertRaises(ValueError): server.approve(p)
    def test_review_rejects_calendar_reset(self):
        p=chat_tasks.parse_task('reschedule the meeting with Priya tomorrow at 4 PM',server.state['meetings'])
        p['calendar_generation']=server.state['generation']
        server.reset()
        with self.assertRaisesRegex(ValueError, 'reset'): server.approve(p)
    def test_injection_scenario_is_blocked(self):
        p=chat_tasks.parse_task('reschedule the meeting with Priya tomorrow at 4 PM',server.state['meetings'])
        server.approve(p)
        results=server.agent('injection')
        self.assertFalse(results[0]['allowed'])
        self.assertEqual(server.state['audit'][-1]['action']['type'],'cancel')
        self.assertTrue(results[-1]['allowed'])

if __name__=='__main__': unittest.main()
