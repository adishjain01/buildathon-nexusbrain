import unittest
import chat_tasks
import server

class ChatTaskTests(unittest.TestCase):
    def setUp(self): server.reset()
    def test_reschedule_task_and_constraints(self):
        p=chat_tasks.parse_task('Reschedule the meeting with Priya this week after 2 PM and never Friday',server.state['meetings'])
        self.assertEqual(p['meeting_id'],'m1')
        self.assertEqual(p['earliest'],'14:01')
        self.assertNotIn(4,p['days'])
        self.assertEqual(p['meeting_version'],1)
    def test_simple_task_and_add_attendee(self):
        self.assertEqual(chat_tasks.parse_task('reschedule the meet with priya this week after 2 PM',server.state['meetings'])['meeting_id'],'m1')
        p=chat_tasks.parse_task('Add Taylor to the meeting with Priya',server.state['meetings'])
        self.assertEqual((p['type'],p['attendee']),('add_attendee','taylor'))
        server.approve(p)
        self.assertTrue(server.gateway({'type':'add_attendee','meeting_id':'m1','attendee':'taylor'})['allowed'])
    def test_missing_date_or_time_is_not_assumed(self):
        for text in ['Reschedule the meeting with Priya', 'Reschedule the meeting with Priya this week']:
            with self.assertRaisesRegex(ValueError, 'What (dates|time)'):
                chat_tasks.parse_task(text,server.state['meetings'])
            self.assertIsNone(server.state['policy'])
    def test_unsupported_or_ambiguous_input_is_rejected(self):
        for text in ['reschedule the meeting with Priya and cancel Alex', 'reschedule the meeting with Priya after lunch', 'reschedule the meeting with someone else']:
            with self.assertRaises(ValueError): chat_tasks.parse_task(text,server.state['meetings'])
    def test_review_rejects_stale_meeting(self):
        p=chat_tasks.parse_task('reschedule the meeting with Priya this week after 2 PM',server.state['meetings'])
        server.state['meetings'][0]['version']+=1
        with self.assertRaises(ValueError): server.approve(p)
    def test_injection_scenario_is_blocked(self):
        p=chat_tasks.parse_task('reschedule the meeting with Priya this week after 2 PM',server.state['meetings'])
        server.approve(p)
        results=server.agent('injection')
        self.assertFalse(results[0]['allowed'])
        self.assertEqual(server.state['audit'][-1]['action']['type'],'cancel')
        self.assertTrue(results[-1]['allowed'])

if __name__=='__main__': unittest.main()
