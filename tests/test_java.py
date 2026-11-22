import json
import os
from pathlib import Path
import subprocess
import threading
import unittest
from tests.local_portal import make_server

ROOT = Path(__file__).resolve().parents[1]


class JavaExecutionTests(unittest.TestCase):
    def test_generated_java(self):
        out = Path((ROOT / 'tmp/latest_verification.txt').read_text(encoding='utf-8'))
        folder = out / 'Java_Playwright'
        maven = next((Path.home() / '.m2/wrapper/dists').rglob('mvn.cmd'))
        server = make_server()
        threading.Thread(target=server.serve_forever, daemon=True).start()
        env = dict(os.environ, BASE_URL=f'http://127.0.0.1:{server.server_port}', PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD='1', BROWSER_CHANNEL='msedge')
        try:
            log_path = ROOT / 'tmp/java_execution.log'
            with log_path.open('w', encoding='utf-8') as log:
                run = subprocess.run([str(maven), '-B', 'test'], cwd=folder, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=300)
            print(log_path.read_text(encoding='utf-8')[-12000:], flush=True)
            # Suite includes one passing journey and one deliberately unresolved journey.
            self.assertEqual(run.returncode, 1)
            reports = sorted((folder / 'execution-reports').glob('*/report-summary.json'))
            self.assertTrue(reports, 'No Java execution report produced')
            data = json.loads(reports[-1].read_text())
            self.assertEqual((data['total'], data['passed'], data['failed']), (2, 1, 1))
            for case in data['test_cases']:
                self.assertTrue(case['trace_rel_path'])
                self.assertTrue((reports[-1].parent / case['trace_rel_path']).is_file())
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    unittest.main()
