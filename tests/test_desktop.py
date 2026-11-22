import tempfile
import time
import unittest
from pathlib import Path
from gui.app_window import EnterpriseQAStudioApp


class DesktopTests(unittest.TestCase):
    def test_demo_and_flow_result_display(self):
        with tempfile.TemporaryDirectory() as output:
            app = EnterpriseQAStudioApp(is_test_mode=True)
            app.withdraw()
            try:
                self.assertEqual(app.tabs.get(), 'Results')
                self.assertFalse(app.advanced_panel.winfo_manager())
                self.assertFalse(app.account_editor.winfo_manager())
                app._toggle_advanced_settings()
                self.assertEqual(app.advanced_panel.winfo_manager(), 'pack')
                app._toggle_advanced_settings()
                app._load_demo_portal()
                self.assertTrue(app.url_entry.get().startswith('http://127.0.0.1:'))
                self.assertEqual(app.profile_dropdown.get(), 'QA')
                app.out_entry.delete(0, 'end')
                app.out_entry.insert(0, output)
                app._on_start_clicked()
                deadline = time.monotonic() + 60
                while app._is_running and time.monotonic() < deadline:
                    app.update()
                    time.sleep(.05)
                self.assertFalse(app._is_running, 'GUI pipeline timed out')
                result = app._cached_final_state
                self.assertIsNotNone(result)
                self.assertEqual(result['inspection_report']['execution_status'], 'passed', result.get('errors'))
                self.assertIn('PASSED', app.status_banner_lbl.cget('text'))
                self.assertIn('PASSED', app.results_textbox.get('0.0', 'end'))
                self.assertTrue((Path(result['output_dir']) / 'Complete-Suite-Test-Report/index.html').exists())
                self.assertEqual(app.out_entry.get(), result['output_dir'])
                # Confirm generation completion does not paint a failed flow green.
                result = dict(result, inspection_report=dict(result['inspection_report'], execution_status='failed'), errors=['Intentional UI test'])
                app._handle_complete_event({'state': result, 'final_state': result})
                self.assertIn('FAILED', app.status_banner_lbl.cget('text'))
            finally:
                app._on_window_close()


if __name__ == '__main__':
    unittest.main()
