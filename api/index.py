"""Vercel adapter for the scripted mock-calendar demo.

Sessions are isolated per browser while a function instance stays warm; a cold
start resets them. This is a demo, not durable storage or production security.
"""
import json
import os
import secrets
import sys
import time
from collections import OrderedDict
from http.cookies import SimpleCookie
from pathlib import Path
from urllib.parse import urlparse

ROOT_DIR = Path(__file__).resolve().parent.parent
INTENT_LOCK_DIR = ROOT_DIR / 'intent-lock'
if str(INTENT_LOCK_DIR) not in sys.path:
    sys.path.insert(0, str(INTENT_LOCK_DIR))
import server

SESSIONS = OrderedDict()
SESSION_TTL = 30 * 60
MAX_SESSIONS = 64

class handler(server.Handler):
    def send_json(self, value, status=200):
        if urlparse(self.path).path == '/api/state' and isinstance(value, dict):
            value = {**value, 'hosted_demo': True, 'openrouter_configured': False}
        return super().send_json(value, status)

    def end_headers(self):
        if hasattr(self, '_cookie_to_set'):
            secure = '; Secure' if os.environ.get('VERCEL') else ''
            self.send_header('Set-Cookie', f'intent_session={self._cookie_to_set}; Path=/; HttpOnly; SameSite=Strict; Max-Age={SESSION_TTL}{secure}')
            self.send_header('Cache-Control', 'no-store')
        super().end_headers()

    def _with_session(self, method):
        # The base gateway uses process-global variables. Hold its re-entrant
        # lock across the short scripted request while binding this browser's
        # separate state; model calls and key handling are disabled here.
        with server.lock:
            now=time.monotonic()
            for key, (_, last) in list(SESSIONS.items()):
                if now-last > SESSION_TTL: del SESSIONS[key]
            cookies=SimpleCookie()
            try: cookies.load(self.headers.get('Cookie', ''))
            except Exception: cookies=SimpleCookie()
            token=cookies['intent_session'].value if 'intent_session' in cookies else ''
            if token not in SESSIONS:
                token=secrets.token_urlsafe(32)
                server.state={}
                server.reset()
                SESSIONS[token]=(server.state,now)
            else:
                server.state=SESSIONS[token][0]
                SESSIONS.move_to_end(token)
                SESSIONS[token]=(server.state,now)
            while len(SESSIONS)>MAX_SESSIONS: SESSIONS.popitem(last=False)
            self._cookie_to_set=token
            original_key=server.openrouter_key
            server.openrouter_key=lambda: ''
            try:
                if urlparse(self.path).path == '/api/key':
                    return self.send_json({'error':'API keys are disabled in the hosted demo. Use scripted mode, or run locally for OpenRouter.'},403)
                return method(self)
            finally:
                server.openrouter_key=original_key

    def do_GET(self):
        if urlparse(self.path).path in ('/api','/api/'):
            return self.send_json({'status':'ok','name':'Intent Lock API','mode':'scripted demo'})
        return self._with_session(server.Handler.do_GET)

    def do_POST(self):
        return self._with_session(server.Handler.do_POST)
