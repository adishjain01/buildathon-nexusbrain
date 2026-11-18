import json
import unittest
from datetime import date, timedelta
import openrouter_agent
import server

class ModelAgentTests(unittest.TestCase):
    def setUp(self):
        server.reset()
        self.policy=server.approve({'type':'add_attendee','meeting_id':'m1','attendee':'Taylor'})
    def test_model_tool_calls_are_checked_and_feedback_returned(self):
        requests=[]
        def fake(payload):
            requests.append(json.loads(json.dumps(payload)))
            attendee='Mallory' if len(requests)==1 else 'Taylor'
            action={'type':'add_attendee','meeting_id':'m1','attendee':attendee}
            return {'choices':[{'message':{'role':'assistant','content':None,'tool_calls':[{'id':str(len(requests)),'type':'function','function':{'name':'calendar_action','arguments':json.dumps(action)}}]}}]}
        result=openrouter_agent.run('unused',self.policy,server.state['meetings'],server.gateway,request_fn=fake)
        self.assertEqual([r['allowed'] for r in result['results']],[False,True])
        self.assertIn('not authorized',requests[1]['messages'][-1]['content'])
        self.assertEqual(server.state['meetings'][0]['attendees'],['you','Priya','Taylor'])
    def test_model_cannot_mutate_without_a_tool_call(self):
        result=openrouter_agent.run('unused',self.policy,server.state['meetings'],server.gateway,request_fn=lambda p:{'choices':[{'message':{'role':'assistant','content':'Done'}}]})
        self.assertEqual(result['results'],[])
        self.assertFalse(server.state['policy']['used'])
        self.assertNotIn('Taylor',server.state['meetings'][0]['attendees'])

if __name__=='__main__': unittest.main()

