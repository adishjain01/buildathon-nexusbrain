import unittest
from datetime import date, timedelta, datetime
import server

class GatewayTests(unittest.TestCase):
    def setUp(self):
        server.reset()
        self.start = date.today() - timedelta(days=date.today().weekday()) + timedelta(days=7)
        self.policy = {'meeting_id':'m1','start_date':self.start.isoformat(),'end_date':(self.start+timedelta(days=6)).isoformat(),'earliest':'14:00','latest':'17:00','days':[0,1,2,3]}
        server.approve(self.policy)
    def action(self, **kw):
        return dict(type='reschedule',meeting_id='m1',date=self.start.isoformat(),time='14:00',**kw)
    def test_blocks_wrong_action_meeting_day_and_extra_fields(self):
        cases = [dict(type='cancel',meeting_id='m1'),dict(type='reschedule',meeting_id='m2',date=self.start.isoformat(),time='14:00'),dict(type='reschedule',meeting_id='m1',date=(self.start+timedelta(days=4)).isoformat(),time='14:00'),self.action(attendees=['you','Mallory'])]
        for action in cases: self.assertFalse(server.gateway(action)['allowed'])
        self.assertEqual(server.state['meetings'][0]['version'],1)
    def test_one_success_and_replay_denied(self):
        self.assertTrue(server.gateway(self.action())['allowed'])
        self.assertFalse(server.gateway(self.action())['allowed'])
        self.assertEqual(server.state['meetings'][0]['attendees'],['you','Priya'])
    def test_collision_and_stale_version(self):
        action = dict(type='reschedule',meeting_id='m1',date=(self.start+timedelta(days=3)).isoformat(),time='15:00')
        server.state['meetings'][1]['date'] = action['date']
        self.assertIn('conflicts',server.gateway(action)['reason'])
        server.state['meetings'][0]['version'] += 1
        self.assertIn('changed',server.gateway(self.action())['reason'])
    def test_expiry_and_reset_revoke(self):
        server.state['policy']['expires_at'] = '2000-01-01T00:00:00'
        self.assertIn('expired',server.gateway(self.action())['reason'])
        server.reset()
        self.assertIn('No active',server.gateway(self.action())['reason'])
    def test_agent_uses_gateway(self):
        results=server.agent('injection')
        self.assertFalse(results[0]['allowed'])
        self.assertTrue(results[-1]['allowed'])
        self.assertGreaterEqual(len(server.state['audit']),3)
    def test_attendee_permission_is_specific_and_single_use(self):
        original = server.state['meetings'][0].copy()
        server.approve({'type':'add_attendee','meeting_id':'m1','attendee':'Taylor'})
        for action in [dict(type='add_attendee',meeting_id='m1',attendee='Mallory'), dict(type='add_attendee',meeting_id='m2',attendee='Taylor'), dict(type='cancel',meeting_id='m1'), dict(type='add_attendee',meeting_id='m1',attendee='Taylor',date='2026-01-01')]:
            self.assertFalse(server.gateway(action)['allowed'])
        good = dict(type='add_attendee',meeting_id='m1',attendee='Taylor')
        self.assertTrue(server.gateway(good)['allowed'])
        self.assertFalse(server.gateway(good)['allowed'])
        self.assertEqual(server.state['meetings'][0]['attendees'], ['you','Priya','Taylor'])
        self.assertEqual(server.state['meetings'][0]['date'], original['date'])
    def test_attendee_approval_rejects_existing_and_empty_names(self):
        for attendee in ['', '  ', 'PRIYA']:
            with self.assertRaises(ValueError): server.approve({'type':'add_attendee','meeting_id':'m1','attendee':attendee})
    def test_attendee_agent_uses_gateway(self):
        server.approve({'type':'add_attendee','meeting_id':'m1','attendee':'Taylor'})
        results = server.agent('injection')
        self.assertEqual([r['allowed'] for r in results], [False, False, False, True])

    def test_simulated_conflict_retries_the_approved_slot(self):
        results=server.agent('conflict')
        self.assertEqual([r['allowed'] for r in results], [False,True])
        self.assertIn('Simulated conflict',results[0]['reason'])
        self.assertEqual(server.state['meetings'][0]['date'],self.start.isoformat())
    def test_normal_agent_does_not_fake_unauthorized_attempts(self):
        results=server.agent('normal')
        self.assertEqual([r['allowed'] for r in results], [True])
    def test_reject_bad_approval(self):
        for update in [{'days':[]},{'days':[True]},{'earliest':'99:99'},{'end_date':(self.start+timedelta(days=40)).isoformat()}]:
            with self.assertRaises(ValueError): server.approve(self.policy | update)

if __name__ == '__main__': unittest.main()
