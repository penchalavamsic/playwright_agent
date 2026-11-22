import ast
import json
import os
from pathlib import Path
import subprocess
import threading
import unittest
from http.server import ThreadingHTTPServer
from datetime import datetime

from core.demo_portal import make_server, DEMO_FLOW
from core.workspace_manager import WorkspaceManager
from tests.test_deployed_auth import AuthSite

ROOT = Path(__file__).resolve().parents[1]


class PackagedTests(unittest.TestCase):
    def test_executable_saved_session_and_loop(self):
        exe = ROOT / 'dist_verified/PlaywrightEnterpriseQAStudio/PlaywrightEnterpriseQAStudio.exe'
        project = ROOT / 'verification_output' / ('packaged-auth-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
        workspace = WorkspaceManager(project)
        workspace.add_or_update_account('QA', 'qa@example.test', 'demo')
        workspace.save_project_state()
        server = ThreadingHTTPServer(('127.0.0.1', 0), AuthSite)
        server.loop, server.login_count = False, 0
        threading.Thread(target=server.serve_forever, daemon=True).start()
        env = {k:v for k,v in os.environ.items() if k not in ('PYTHONPATH','PYTHONHOME')}
        args = [str(exe), '--cli', '--url', f'http://127.0.0.1:{server.server_port}/login',
                '--flow', 'Login as QA; verify "Dashboard"', '--profile', 'QA', '--output', str(project),
                '--auth-success-path', '/dashboard', '--auth-timeout', '5', '--auth-settle', '1']
        try:
            for mode, expected in [('persistent', 0), ('persistent', 0), ('fresh', 1)]:
                server.loop = expected == 1
                run = subprocess.run(args+['--session-mode', mode], cwd=ROOT/'tmp', env=env, text=True, capture_output=True, timeout=90)
                self.assertEqual(run.returncode, expected, run.stdout+run.stderr)
                self.assertEqual(server.login_count, 2 if server.loop else 1)
            data = json.loads((project/'Complete-Suite-Test-Report/report-summary.json').read_text())
            self.assertEqual((data['passed'], data['failed']), (2, 1))
            case = [case for case in data['test_cases'] if case['status'] == 'failed'][0]
            self.assertIn('Login loop detected', case['auth_diagnostics']['error'])
            self.assertEqual(case['auth_diagnostics']['unauthorized_responses'][0]['status'], 401)
        finally:
            server.shutdown()
            server.server_close()

    def test_executable_flow_and_reports(self):
        exe = ROOT / 'dist_verified/PlaywrightEnterpriseQAStudio/PlaywrightEnterpriseQAStudio.exe'
        self.assertTrue(exe.is_file())
        project = ROOT / 'verification_output' / ('packaged-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
        workspace = WorkspaceManager(project)
        workspace.add_or_update_account('QA', 'qa@example.test', 'local-demo-only')
        workspace.save_project_state()
        server = make_server()
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}'
        env = {k:v for k,v in os.environ.items() if k not in ('PYTHONPATH','PYTHONHOME')}
        try:
            for flow, expected_code in ((DEMO_FLOW, 0), ('Login as QA; click "Missing button"', 1)):
                run = subprocess.run([str(exe), '--cli', '--url', url, '--flow', flow, '--profile', 'QA', '--output', str(project)], cwd=ROOT / 'tmp', env=env, text=True, capture_output=True, timeout=90)
                print(run.stdout[-3000:], run.stderr[-1500:], flush=True)
                self.assertEqual(run.returncode, expected_code)
            report_dir = project / 'Complete-Suite-Test-Report'
            data = json.loads((report_dir / 'report-summary.json').read_text())
            self.assertEqual((data['total'], data['passed'], data['failed']), (6, 1, 1))
            self.assertEqual(data['schema_version'], 2)
            for case in (data['test_cases'][0], data['test_cases'][3]):
                for key in ('final_screenshot','trace_rel_path','video_rel_path'):
                    self.assertTrue(case[key], key + ' was not captured by packaged app')
                    self.assertGreater((report_dir / case[key]).stat().st_size, 1000)
            for source in (project / 'Python_Playwright').rglob('*.py'):
                ast.parse(source.read_text(encoding='utf-8'))
            (ROOT / 'tmp/latest_packaged.txt').write_text(str(project), encoding='utf-8')
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    unittest.main()
