import asyncio
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import AsyncMock, patch

from core.flow_parser import parse_flow
from core.browser_inspector import BrowserInspector
from core.report_generator import EnterpriseReportGenerator
from agents.workflow_graph import run_agent_pipeline
from tests.local_portal import make_server

FLOW = 'Login as QA; click "Tasks"; click "New task"; fill "Title" with "Office QA task"; select "High" from "Priority"; check "Notify team"; click "Create task"; verify API "/api/tasks" status code 201; verify "Task created"'
CREDENTIALS = {'QA': {'username': 'qa@example.test', 'password': 'local-demo-only'}}


class ParserTests(unittest.TestCase):
    def test_order_and_quoted_values(self):
        steps = parse_flow('fill "Title" with "Research, design and verify" and click "Save" then verify "Saved"', 'http://localhost')
        self.assertEqual([s['action_type'] for s in steps], ['NAVIGATE', 'FILL', 'CLICK', 'VERIFY_UI'])
        self.assertEqual(steps[1]['input_value'], 'Research, design and verify')

    def test_unknown_is_retained(self):
        self.assertEqual(parse_flow('do something magical')[0]['action_type'], 'UNSUPPORTED')

    def test_checkbox_and_literal_punctuation(self):
        steps = parse_flow('check "Notify team"; fill "Title" with "Version 1.0."')
        self.assertEqual(steps[0]['action_type'], 'CHECK')
        self.assertEqual(steps[1]['input_value'], 'Version 1.0.')

    def test_numbered_flow_and_role(self):
        steps = parse_flow('1. Login as super user\n2. click the "Tasks" button')
        self.assertEqual(steps[0]['target_keyword'], 'SUPER_USER')
        self.assertEqual(steps[1]['target_keyword'], 'Tasks')

    def test_report_without_execution_has_no_fake_evidence(self):
        with tempfile.TemporaryDirectory() as temp:
            EnterpriseReportGenerator(temp).generate_from_agent_state({'test_scenarios': [{'title': 'Unexecuted', 'steps': []}]})
            data = json.loads((Path(temp) / 'Complete-Suite-Test-Report/report-summary.json').read_text())
            self.assertEqual(data['passed'], 0)
            self.assertEqual(data['test_cases'][0]['status'], 'not_run')
            self.assertFalse(list(Path(temp).rglob('*.png')))
            self.assertFalse(list(Path(temp).rglob('*.webm')))
            self.assertFalse(list(Path(temp).rglob('*.zip')))

    def test_browser_launch_failure_still_produces_failed_report(self):
        with tempfile.TemporaryDirectory() as temp, patch('agents.workflow_graph.BrowserInspector.inspect_url', new=AsyncMock(side_effect=RuntimeError('Browser blocked by policy'))):
            result = asyncio.run(run_agent_pipeline(dict(target_url='localhost:8765', user_flow_text='click "Tasks"', output_dir=temp, generate_scripts=False)))
            self.assertEqual(result['target_url'], 'http://localhost:8765')
            self.assertEqual(result['inspection_report']['execution_status'], 'failed')
            summary = json.loads((Path(result['output_dir']) / 'Complete-Suite-Test-Report/report-summary.json').read_text())
            self.assertEqual(summary['failed'], 1)
            self.assertIn('Browser blocked by policy', summary['test_cases'][0]['error_message'])

    def test_legacy_false_pass_is_not_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            report_dir = Path(temp) / 'Complete-Suite-Test-Report'
            report_dir.mkdir()
            summary_path = report_dir / 'report-summary.json'
            summary_path.write_text(json.dumps({'test_cases': [{'test_id':'OLD-001','status':'passed','duration_s':4}]}))
            EnterpriseReportGenerator(temp).generate_from_agent_state({})
            summary = json.loads(summary_path.read_text())
            self.assertEqual(summary['passed'], 0)
            self.assertEqual(summary['test_cases'][0]['status'], 'not_run')
            self.assertEqual(summary['test_cases'][0]['legacy_reported_status'], 'passed')


class LiveFlowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server()
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def inspect(self, flow, credentials=None):
        return asyncio.run(BrowserInspector().inspect_url(self.url, flow, account_credentials=credentials or CREDENTIALS, active_access_profile='QA'))

    def test_full_flow_and_real_evidence(self):
        report = self.inspect(FLOW)
        self.assertEqual(report.execution_status, 'passed', report.execution_steps)
        self.assertTrue(report.login_performed)
        self.assertTrue(report.final_url.endswith('/tasks/created'))
        self.assertEqual(len(report.execution_steps), 10)
        self.assertTrue(Path(report.final_screenshot_path).stat().st_size > 5000)
        self.assertTrue(Path(report.trace_path).stat().st_size > 1000)

    def test_failed_target_stops_dependent_actions(self):
        report = self.inspect('Login as QA; click "Missing button"; click "Tasks"')
        self.assertEqual([r['status'] for r in report.execution_steps], ['passed', 'passed', 'failed', 'skipped'])

    def test_failed_login_is_not_success(self):
        report = self.inspect('Login as QA; click "Tasks"', {'QA': {'username': 'qa@example.test', 'password': 'wrong'}})
        self.assertFalse(report.login_performed)
        self.assertEqual(report.execution_status, 'failed')
        self.assertEqual(report.execution_steps[-1]['status'], 'skipped')

    def test_api_failure_not_hidden_by_successful_login(self):
        report = self.inspect('Login as QA; click "Tasks"; click "Broken API"; verify API "/api/broken" status code 200')
        self.assertEqual(report.execution_status, 'failed')
        self.assertIn('503', report.execution_steps[-1]['error'])


if __name__ == '__main__':
    unittest.main()
