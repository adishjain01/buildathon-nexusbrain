import sys
import os
from pathlib import Path
from urllib.parse import urlparse

# Ensure intent-lock module is importable
ROOT_DIR = Path(__file__).resolve().parent.parent
INTENT_LOCK_DIR = ROOT_DIR / 'intent-lock'
if str(INTENT_LOCK_DIR) not in sys.path:
    sys.path.insert(0, str(INTENT_LOCK_DIR))

import server

# Ensure initial calendar state is populated
if not server.state.get('meetings'):
    server.reset()

class handler(server.Handler):
    def do_GET(self):
        req_path = urlparse(self.path).path
        if req_path in ('/api', '/api/'):
            self.send_json({
                'status': 'ok',
                'name': 'Intent Lock API',
                'description': 'Deterministic boundary gateway protecting calendar state from unauthorized LLM actions'
            })
            return
        super().do_GET()

    def do_POST(self):
        super().do_POST()
