#!/usr/bin/env python3
"""Ava-Nav admin server — exposes git pull/status/log over HTTP for the browser UI.

Run on the Pi:  python3 ava-admin.py
Then use the Admin tab in Ava-Nav to pull updates without opening a terminal.
"""

import http.server, json, subprocess, os

REPO = os.path.dirname(os.path.abspath(__file__))
PORT = 8082


class Handler(http.server.BaseHTTPRequestHandler):

    def do_OPTIONS(self):
        self._cors()
        self.end_headers()

    def do_GET(self):
        if   self.path == '/health': self._json({'ok': True})
        elif self.path == '/status': self._run(['git', 'status', '--short'])
        elif self.path == '/log':    self._run(['git', 'log', '--oneline', '-12'])
        else: self.send_response(404); self.end_headers()

    def do_POST(self):
        if   self.path == '/pull': self._run(['git', 'pull'])
        else: self.send_response(404); self.end_headers()

    def _run(self, cmd):
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, cwd=REPO, timeout=30)
            self._json({'ok': True, 'stdout': r.stdout, 'stderr': r.stderr, 'rc': r.returncode})
        except Exception as e:
            self._json({'ok': False, 'error': str(e)})

    def _json(self, data):
        body = json.dumps(data).encode()
        self._cors()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def log_message(self, *a):
        pass  # suppress per-request console noise


if __name__ == '__main__':
    print(f'Ava-Nav admin server listening on :{PORT}  (repo: {REPO})')
    with http.server.HTTPServer(('', PORT), Handler) as srv:
        srv.serve_forever()
