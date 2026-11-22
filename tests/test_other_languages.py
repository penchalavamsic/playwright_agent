"""Replay the generated projects using locally installed test dependencies."""
import json
import os
from pathlib import Path
import subprocess
import threading
import unittest
from tests.local_portal import make_server

ROOT = Path(__file__).resolve().parents[1]


class OtherLanguageTests(unittest.TestCase):
    def test_generated_js_and_ts(self):
        out = Path((ROOT / 'tmp/latest_verification.txt').read_text(encoding='utf-8'))
        server = make_server()
        threading.Thread(target=server.serve_forever, daemon=True).start()
        env = dict(os.environ, BASE_URL=f'http://127.0.0.1:{server.server_port}', NODE_PATH=str(ROOT / 'tmp/js_runtime/node_modules'))
        cli = ROOT / 'tmp/js_runtime/node_modules/@playwright/test/cli.js'
        try:
            for language in ('JavaScript', 'TypeScript'):
                folder = out / (language + '_Playwright')
                run = subprocess.run(['node', str(cli), 'test', '001_', '--workers=1'], cwd=folder, env=env, text=True, capture_output=True, timeout=90)
                print(run.stdout, run.stderr, flush=True)
                self.assertEqual(run.returncode, 0, language)
                run = subprocess.run(['node', str(cli), 'test', '002_', '--workers=1'], cwd=folder, env=env, text=True, capture_output=True, timeout=90)
                print(run.stdout, run.stderr, flush=True)
                self.assertEqual(run.returncode, 1, language)
                reports = sorted((folder / 'execution-reports').glob('*/report-summary.json'))
                self.assertEqual(json.loads(reports[-1].read_text())['failed'], 1)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    unittest.main()
