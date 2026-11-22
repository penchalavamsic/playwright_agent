import asyncio
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import tempfile
import threading
import unittest
import ssl

from core.browser_inspector import BrowserInspector
from core.browser_session import matches_path, profile_directory, safe_url


class AuthSite(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send(self, body, status=200, cookie=None):
        self.send_response(status)
        self.send_header('Content-Type', 'text/html')
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        authenticated = 'qa_session=valid' in self.headers.get('Cookie', '')
        if self.path == '/login' and authenticated:
            self.send_response(302)
            self.send_header('Location', '/dashboard')
            self.end_headers()
        elif self.path == '/dashboard':
            if not authenticated:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            script = "setTimeout(()=>{location.href='/expire'},350)" if self.server.loop else ''
            self.send('<h1>Dashboard</h1><button id="expire" onclick="location.href=\'/expire\'">Expire session</button><script>' + script + '</script>')
        elif self.path == '/expire':
            self.send('<script>fetch("/unauthorized").then(()=>location.href="/login")</script>', cookie='qa_session=; Max-Age=0; Path=/')
        elif self.path == '/unauthorized':
            self.send('Session expired', 401)
        else:
            form = '<h1>Login</h1><form><label>Email<input type="email"></label><label>Password<input type="password"></label><button type="submit">Sign in</button></form>'
            handler = "document.querySelector('form').onsubmit=async e=>{e.preventDefault();await fetch('/session',{method:'POST'});location.href='/dashboard'}"
            if getattr(self.server, 'delayed', False):
                self.send('<h1>Loading</h1><script>setTimeout(()=>{document.body.innerHTML=' + json.dumps(form) + ';' + handler + '},900)</script>')
            else:
                self.send(form + '<script>' + handler + '</script>')

    def do_POST(self):
        self.server.login_count += 1
        cookie = 'qa_session=valid; Max-Age=3600; Path=/; HttpOnly; SameSite=Lax'
        self.send('{}', cookie=cookie + ('; Secure' if getattr(self.server, 'secure', False) else ''))


class DeployedAuthTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), AuthSite)
        self.server.loop, self.server.login_count = False, 0
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f'http://127.0.0.1:{self.server.server_port}/login'
        self.temp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.temp.cleanup()

    def run_flow(self, mode='fresh', credentials=True, flow='Login as QA; verify "Dashboard"'):
        return asyncio.run(BrowserInspector().inspect_url(self.url, flow, active_access_profile='QA',
            account_credentials={'QA': {'username':'qa@example.test', 'password':'demo'}} if credentials else {},
            session_root=self.temp.name, browser_settings={'session_mode':mode, 'auth_success_path':'/dashboard', 'auth_timeout_ms':5000, 'auth_settle_ms':1000}))

    def test_fresh_context_and_stable_login(self):
        self.assertEqual(self.run_flow().execution_status, 'passed')
        self.assertEqual(self.run_flow().execution_status, 'passed')
        self.assertEqual(self.server.login_count, 2)

    def test_persistent_profile_reuses_cookie_without_resubmitting(self):
        self.assertEqual(self.run_flow('persistent').execution_status, 'passed')
        result = self.run_flow('persistent', credentials=False)
        self.assertEqual(result.execution_status, 'passed', result.execution_steps)
        self.assertEqual(self.server.login_count, 1)

    def test_login_dashboard_login_loop_stops_after_one_attempt(self):
        self.server.loop = True
        report = self.run_flow()
        self.assertEqual(report.execution_status, 'failed')
        self.assertIn('Login loop detected', report.execution_steps[1]['error'])
        self.assertEqual(report.execution_steps[-1]['status'], 'skipped')
        self.assertEqual(self.server.login_count, 1)
        self.assertEqual(report.auth_diagnostics['unauthorized_responses'][0]['status'], 401)

    def test_session_loss_mid_flow(self):
        report = self.run_flow(flow='Login as QA; click "Expire session"; verify "Dashboard"')
        self.assertEqual(report.execution_status, 'failed')
        self.assertIn('Session lost', report.execution_steps[2]['error'])
        self.assertEqual(self.server.login_count, 1)

    def test_delayed_spa_login_form(self):
        self.server.delayed = True
        self.assertEqual(self.run_flow().execution_status, 'passed')
        self.assertEqual(self.server.login_count, 1)

    def test_diagnostics_and_profile_isolation(self):
        self.assertEqual(safe_url('https://user:secret@app.test/login?token=secret#token'), 'https://app.test/login')
        self.assertFalse(matches_path('https://app.test/login?next=/dashboard','/dashboard'))
        self.assertNotEqual(profile_directory(self.temp.name, self.url, 'QA', 'msedge'), profile_directory(self.temp.name, self.url, 'ADMIN', 'msedge'))

    def test_https_secure_cookie_redirects(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), AuthSite)
        server.loop, server.login_count, server.secure = False, 0, True
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        fixtures = Path(__file__).parent / 'fixtures'
        context.load_cert_chain(fixtures/'localhost-cert.pem', fixtures/'localhost-key.pem')
        server.socket = context.wrap_socket(server.socket, server_side=True)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        self.url = f'https://127.0.0.1:{server.server_port}/login'
        try:
            report = self.run_flow()
            self.assertEqual(report.execution_status, 'passed', report.execution_steps)
            self.assertTrue(report.final_url.startswith('https://'))
            self.assertEqual(server.login_count, 1)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    unittest.main()
