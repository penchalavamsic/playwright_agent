"""Exercise actual generated runners against a cookie-authenticated web server."""
import asyncio
from datetime import datetime
from http.server import ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import unittest

from agents.workflow_graph import run_agent_pipeline
from tests.test_deployed_auth import AuthSite

ROOT = Path(__file__).resolve().parents[1]


class GeneratedSessionTests(unittest.TestCase):
    def test_saved_sessions_and_login_loop_in_all_runners(self):
        server = ThreadingHTTPServer(('127.0.0.1', 0), AuthSite)
        server.loop, server.login_count, server.delayed = False, 0, True
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}/login'
        config = dict(session_mode='persistent', auth_success_path='/dashboard', auth_timeout_ms=5000, auth_settle_ms=1000)
        env = dict(os.environ, BASE_URL=url, BROWSER_CHANNEL='msedge', PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD='1', NODE_PATH=str(ROOT/'tmp/js_runtime/node_modules'))
        try:
            result = asyncio.run(run_agent_pipeline(dict(target_url=url, user_flow_text='Login as QA; verify "Dashboard"',
                headless=True, target_languages=['Python', 'JavaScript', 'TypeScript', 'Java'],
                active_access_profile='QA', account_credentials={'QA':dict(username='qa@example.test', password='demo')},
                browser_settings=config, output_dir=str(ROOT/'verification_output'/('sessions-'+datetime.now().strftime('%Y%m%d-%H%M%S'))),
                generate_scripts=True, generate_test_plan=True, errors=[], generated_files=[])))
            self.assertFalse(result['errors'], result['errors'])
            out = Path(result['output_dir'])
            maven = next((Path.home()/'.m2/wrapper/dists').rglob('mvn.cmd'))
            commands = {
                'Python': [sys.executable, '-m', 'pytest'],
                'JavaScript': ['node', str(ROOT/'tmp/js_runtime/node_modules/@playwright/test/cli.js'), 'test', '--workers=1'],
                'TypeScript': ['node', str(ROOT/'tmp/js_runtime/node_modules/@playwright/test/cli.js'), 'test', '--workers=1'],
                'Java': [str(maven), '-B', 'test'],
            }
            for language, command in commands.items():
                with self.subTest(language=language):
                    folder = out/(language+'_Playwright')
                    server.loop = False
                    (out/'browser-settings.json').write_text(json.dumps(config), encoding='utf-8')
                    count = server.login_count
                    for repeat in range(2):
                        run = subprocess.run(command, cwd=folder, env=env, text=True, capture_output=True, timeout=180)
                        (ROOT/'tmp'/f'sessions-{language}-{repeat}.log').write_text(run.stdout+run.stderr, encoding='utf-8')
                        self.assertEqual(run.returncode, 0, run.stdout[-4000:]+run.stderr[-1000:])
                        self.assertEqual(server.login_count, count+1, 'Saved session unexpectedly resubmitted login')
                        report = sorted((folder/'execution-reports').glob('*/report-summary.json'))[-1]
                        data = json.loads(report.read_text())
                        self.assertEqual(data['passed'], 1)
                        self.assertTrue(data['test_cases'][0]['trace_rel_path'])
                    server.loop = True
                    (out/'browser-settings.json').write_text(json.dumps(dict(config, session_mode='fresh')), encoding='utf-8')
                    run = subprocess.run(command, cwd=folder, env=env, text=True, capture_output=True, timeout=180)
                    (ROOT/'tmp'/f'sessions-{language}-loop.log').write_text(run.stdout+run.stderr, encoding='utf-8')
                    self.assertNotEqual(run.returncode, 0)
                    self.assertEqual(server.login_count, count+2, 'Login loop triggered a retry')
                    report = sorted((folder/'execution-reports').glob('*/report-summary.json'))[-1]
                    data = json.loads(report.read_text())
                    self.assertEqual(data['failed'], 1)
                    self.assertIn('Login loop detected', data['test_cases'][0]['error_message'])
                    print(f'{language}: delayed login passed, saved cookie reused, loop stopped after one attempt.', flush=True)
            print(f'Session artifacts: {out}', flush=True)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    unittest.main()
