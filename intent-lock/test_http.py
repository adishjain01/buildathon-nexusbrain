import json
import threading
import unittest
from datetime import date, timedelta
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
import server

class HttpDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        server.reset()
        cls.httpd = ThreadingHTTPServer(('127.0.0.1', 0), server.Handler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = 'http://127.0.0.1:%d' % cls.httpd.server_port
    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown(); cls.httpd.server_close(); cls.thread.join()
    def request(self, path, body=None):
        req = Request(self.base+path, data=None if body is None else json.dumps(body).encode(), headers={'Content-Type':'application/json'})
        with urlopen(req, timeout=5) as res: return res.read().decode()
    def test_live_http_workflow(self):
        self.assertIn('intent lock', self.request('/'))
        self.assertIn('apply-constraint', self.request('/app.js'))
        today=date.today(); end=today+timedelta(days=6)
        p={'meeting_id':'m1','start_date':today.isoformat(),'end_date':end.isoformat(),'earliest':'14:01','latest':'17:00','days':[0,1,2,3]}
        self.request('/api/approve',p)
        blocked=json.loads(self.request('/api/action',{'type':'add_attendee','meeting_id':'m1','attendee':'Mallory'}))
        self.assertFalse(blocked['allowed'])
        results=json.loads(self.request('/api/agent',{}))
        self.assertTrue(results[-1]['allowed'])
        self.assertTrue(json.loads(self.request('/api/state'))['policy']['used'])
        self.request('/api/reset',{})
        self.assertIsNone(json.loads(self.request('/api/state'))['policy'])
    def test_session_key_is_not_exposed_and_cross_origin_is_rejected(self):
        key = 'test-session-key-not-a-real-secret'
        try:
            self.assertTrue(json.loads(self.request('/api/key', {'key':key}))['session_key_set'])
            state = self.request('/api/state')
            self.assertNotIn(key, state)
            self.assertTrue(json.loads(state)['openrouter_configured'])
            req = Request(self.base+'/api/key', data=b'{"key":""}', headers={'Content-Type':'application/json','Origin':'http://example.com'})
            with self.assertRaises(HTTPError) as error: urlopen(req, timeout=5)
            self.assertEqual(error.exception.code,403)
            self.assertEqual(server.session_key,key)
        finally:
            self.request('/api/key', {'key':''})
        self.assertEqual(server.session_key,'')

if __name__ == '__main__': unittest.main()
