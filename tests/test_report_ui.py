import json
from pathlib import Path
import unittest
import zipfile
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class ReportUiTests(unittest.TestCase):
    def test_packaged_recording_plays(self):
        pointer = ROOT / 'tmp/latest_packaged.txt'
        if not pointer.exists():
            self.skipTest('Run tests.test_packaged first to produce a packaged recording.')
        report = Path(pointer.read_text(encoding='utf-8')) / 'Complete-Suite-Test-Report'
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel='msedge', headless=True)
            page = browser.new_page(viewport={'width':1280, 'height':900})
            page.goto((report / 'index.html').as_uri())
            page.locator('.test-header').first.click()
            page.locator('img').evaluate_all('(images) => images.forEach(img => img.loading = "eager")')
            page.wait_for_function('Array.from(document.images).every(img => img.complete && img.naturalWidth > 0)', timeout=10000)
            video = page.locator('video').first
            video.evaluate('(video) => { video.muted = true; return video.play(); }')
            page.wait_for_function('document.querySelector("video").currentTime > 0 && document.querySelector("video").videoWidth > 0', timeout=10000)
            video.evaluate('(video) => video.pause()')
            video.scroll_into_view_if_needed()
            page.screenshot(path=str(ROOT / 'verification_output/packaged-video-playback.png'))
            self.assertEqual(video.evaluate('(video) => video.error'), None)
            browser.close()

    def test_offline_report_media_filters_and_layout(self):
        out = Path((ROOT / 'tmp/latest_verification.txt').read_text(encoding='utf-8'))
        report = out / 'Complete-Suite-Test-Report'
        data = json.loads((report / 'report-summary.json').read_text())
        with sync_playwright() as pw:
            browser = pw.chromium.launch(channel='msedge', headless=True)
            page = browser.new_page(viewport={'width':1280,'height':900})
            errors = []
            page.on('pageerror', lambda exc: errors.append(str(exc)))
            page.goto((report / 'index.html').as_uri())
            self.assertEqual(page.locator('.test-card').count(), 6)
            page.get_by_role('button', name='Failed (1)', exact=True).click()
            self.assertEqual(page.locator('.test-card:visible').count(), 1)
            page.locator('#card-search').fill('Primary')
            self.assertEqual(page.locator('.test-card:visible').count(), 1)
            page.locator('#card-search').fill('No such report')
            self.assertEqual(page.locator('.test-card:visible').count(), 0)
            page.locator('#card-search').fill('')
            page.get_by_role('button', name='All (6)', exact=True).click()
            page.locator('.test-header').first.click()
            page.screenshot(path=str(ROOT / 'verification_output/report-desktop.png'))
            for case in data['test_cases']:
                for key in ('final_screenshot', 'trace_rel_path', 'video_rel_path'):
                    if case[key]:
                        self.assertTrue((report / case[key]).is_file())
                if case['trace_rel_path']:
                    with zipfile.ZipFile(report / case['trace_rel_path']) as trace:
                        self.assertTrue(any(n.endswith('.trace') for n in trace.namelist()))
            for width in (1280, 390):
                page.set_viewport_size({'width':width,'height':900})
                self.assertTrue(page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
            page.screenshot(path=str(ROOT / 'verification_output/report-mobile.png'))
            self.assertFalse(errors)
            browser.close()


if __name__ == '__main__':
    unittest.main()
