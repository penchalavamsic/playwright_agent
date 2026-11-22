import asyncio
import ast
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import unittest
from datetime import datetime

from agents.workflow_graph import run_agent_pipeline
from tests.local_portal import make_server
from tests.test_flow_regressions import FLOW, CREDENTIALS

ROOT = Path(__file__).resolve().parents[1]


class GeneratedExecutionTests(unittest.TestCase):
    def test_pipeline_and_generated_python(self):
        server = make_server()
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_port}'
        try:
            result = asyncio.run(run_agent_pipeline(dict(
                target_url=url, user_flow_text=FLOW, headless=True,
                target_languages=['Python','Java','TypeScript','JavaScript'],
                output_dir=str(ROOT / 'verification_output' / datetime.now().strftime('%Y%m%d-%H%M%S')),
                active_access_profile='QA', account_credentials=CREDENTIALS,
                generate_scripts=True, generate_test_plan=True, errors=[], generated_files=[])))
            self.assertFalse(result['errors'], result['errors'])
            out = Path(result['output_dir'])
            (ROOT / 'tmp/latest_verification.txt').write_text(str(out), encoding='utf-8')
            summary_path = out / 'Complete-Suite-Test-Report/report-summary.json'
            before = summary_path.read_bytes()
            summary = json.loads(before)
            self.assertEqual((summary['passed'], summary['failed'], summary['skipped']), (1, 0, 2))
            py_root = out / 'Python_Playwright'
            for source in py_root.rglob('*.py'):
                ast.parse(source.read_text(encoding='utf-8'), filename=str(source))
            process = subprocess.run([sys.executable, '-m', 'pytest'], cwd=py_root, text=True, capture_output=True, timeout=90)
            print(process.stdout, process.stderr, flush=True)
            self.assertEqual(process.returncode, 0)
            execution = json.loads(next((py_root / 'execution-reports').glob('*/report-summary.json')).read_text())
            self.assertEqual(execution['passed'], 1)
            self.assertTrue(execution['test_cases'][0]['trace_rel_path'])
            self.assertEqual(before, summary_path.read_bytes(), 'Rerun overwrote inspection evidence')
            # Persist a second run with an intentional failure, without overwriting run 1.
            failed = asyncio.run(run_agent_pipeline(dict(result, user_flow_text='Login as QA; click "Does not exist"; click "Tasks"', sequence_number=2)))
            data = json.loads(summary_path.read_text())
            self.assertEqual((data['total'], data['passed'], data['failed']), (6, 1, 1))
            env = dict(os.environ, BASE_URL=url)
            process = subprocess.run([sys.executable, '-m', 'pytest', *[str(p.relative_to(py_root)) for p in (py_root / 'tests').glob('002_*.py')]], cwd=py_root, text=True, capture_output=True, timeout=90, env=env)
            print(process.stdout, process.stderr, flush=True)
            self.assertEqual(process.returncode, 1)
            reports = sorted((py_root / 'execution-reports').glob('*/report-summary.json'))
            self.assertEqual(json.loads(reports[-1].read_text())['failed'], 1)
            # Browser fixture/setup errors must appear in the report, even if the test body never ran.
            env['BROWSER_CHANNEL'] = 'deliberately-invalid-channel'
            process = subprocess.run([sys.executable, '-m', 'pytest', *[str(p.relative_to(py_root)) for p in (py_root / 'tests').glob('001_*.py')]], cwd=py_root, text=True, capture_output=True, timeout=90, env=env)
            self.assertEqual(process.returncode, 1)
            reports = sorted((py_root / 'execution-reports').glob('*/report-summary.json'))
            setup_report = json.loads(reports[-1].read_text())
            self.assertEqual(setup_report['failed'], 1)
            self.assertIn('setup:', setup_report['test_cases'][0]['error_message'])
            self.assertFalse(setup_report['test_cases'][0]['video_rel_path'])
            print(f'Artifacts: {out}', flush=True)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == '__main__':
    unittest.main()
