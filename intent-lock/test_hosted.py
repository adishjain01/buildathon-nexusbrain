import http.cookiejar
import importlib.util
import json
import threading
import unittest
from datetime import date, timedelta
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import HTTPCookieProcessor, Request, build_opener

spec=importlib.util.spec_from_file_location('vercel_adapter', Path(__file__).resolve().parent.parent/'api'/'index.py')
adapter=importlib.util.module_from_spec(spec)
spec.loader.exec_module(adapter)

class HostedSessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd=ThreadingHTTPServer(('127.0.0.1',0),adapter.handler)
        cls.thread=threading.Thread(target=cls.httpd.serve_forever,daemon=True)
        cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.httpd.server_port}'
    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown();cls.httpd.server_close();cls.thread.join()
    def client(self): return build_opener(HTTPCookieProcessor(http.cookiejar.CookieJar()))
    def request(self, client, path, data=None):
        req=Request(self.base+path,data=None if data is None else json.dumps(data).encode(),headers={'Content-Type':'application/json'})
        with client.open(req,timeout=5) as response: return json.load(response)
    def test_browser_sessions_are_isolated_and_cold_start_resets(self):
        a,b=self.client(),self.client()
        a1=self.request(a,'/api/state');b1=self.request(b,'/api/state')
        self.assertNotEqual(a1['generation'],b1['generation'])
        self.assertTrue(a1['hosted_demo']);self.assertFalse(a1['openrouter_configured'])
        self.request(a,'/api/approve',{'type':'add_attendee','meeting_id':'m1','attendee':'Taylor'})
        self.assertTrue(self.request(a,'/api/action',{'type':'add_attendee','meeting_id':'m1','attendee':'Taylor'})['allowed'])
        self.assertIn('Taylor',self.request(a,'/api/state')['meetings'][0]['attendees'])
        self.assertNotIn('Taylor',self.request(b,'/api/state')['meetings'][0]['attendees'])
        adapter.SESSIONS.clear()
        self.assertNotIn('Taylor',self.request(a,'/api/state')['meetings'][0]['attendees'])
    def test_hosted_key_input_is_disabled(self):
        with self.assertRaises(HTTPError) as error:
            self.request(self.client(),'/api/key',{'key':'fake-test-key'})
        self.assertEqual(error.exception.code,403)
    def test_rewritten_vercel_endpoint_restores_original_route(self):
        client=self.client()
        state=self.request(client,'/api/index.py?intent_route=state')
        self.assertTrue(state['hosted_demo'])
        self.assertEqual(len(state['meetings']),3)
        self.assertTrue(self.request(client,'/api/index.py?intent_route=reset',{})['ok'])

if __name__=='__main__':unittest.main()
