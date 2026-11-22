from pathlib import Path
import json
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT/'demo_media/assets'
REPORT = ROOT/'demo_media/project/Complete-Suite-Test-Report'
FAILED_REPORT = os.environ.get('FAILED_REPORT')
if not FAILED_REPORT:
    raise SystemExit('Set FAILED_REPORT to the local failed-authentication report index.html.')

def clean_view(page):
    # Presentation-only removal; original reports and result data stay unchanged.
    page.evaluate("""() => {
      document.querySelectorAll('.summary-card').forEach(card => {
        if (['Date','Duration'].includes(card.querySelector('.summary-label')?.textContent.trim())) card.style.display='none';
      });
      document.querySelectorAll('.test-duration').forEach(el=>el.style.display='none');
    }""")
    page.add_style_tag(content='*{scrollbar-width:none!important} ::-webkit-scrollbar{display:none!important} .report-header h1{font-size:24px} .container{max-width:1440px}')

def settle_media(page):
    page.locator('img').evaluate_all('(images)=>images.forEach(img=>img.loading="eager")')
    page.wait_for_function('Array.from(document.images).every(img=>img.complete)')
    page.wait_for_timeout(500)

with sync_playwright() as pw:
    browser = pw.chromium.launch(channel='msedge', headless=True)
    page = browser.new_page(viewport={'width':1440,'height':860}, device_scale_factor=1)
    page.goto((REPORT/'index.html').as_uri())
    clean_view(page)
    page.screenshot(path=str(ASSETS/'11-report-overview.png'))
    page.get_by_role('button',name='Passed (1)',exact=True).click()
    page.locator('.test-header').first.click()
    settle_media(page)
    page.locator('.steps').first.screenshot(path=str(ASSETS/'12-report-steps.png'))
    page.locator('img').evaluate_all('(images)=>images.forEach(img=>img.loading="eager")')
    page.wait_for_function('Array.from(document.images).every(img=>img.complete)')
    page.locator('.api-summary').first.screenshot(path=str(ASSETS/'13-api-summary.png'))
    # A focused section showing the real video and trace/download controls.
    video = page.locator('video').first
    video.evaluate('(v)=>{v.currentTime=Math.max(0,v.duration-.5);v.pause()}')
    video.scroll_into_view_if_needed()
    page.screenshot(path=str(ASSETS/'14-evidence.png'))
    case = json.loads((REPORT/'report-summary.json').read_text())['test_cases'][0]
    (ASSETS/'evidence.json').write_text(json.dumps({'video':str(REPORT/case['video_rel_path']), 'screenshot':str(REPORT/case['final_screenshot']), 'trace':str(REPORT/case['trace_rel_path'])}, indent=2))
    failed_report = Path(FAILED_REPORT).resolve()
    page.goto(failed_report.as_uri())
    clean_view(page)
    page.get_by_role('button',name='Failed (1)',exact=True).click()
    failed = page.locator('.test-card.failed')
    failed.locator('.test-header').click()
    settle_media(page)
    failed.locator('.auth-diagnostics').scroll_into_view_if_needed()
    page.wait_for_timeout(300)
    failed.locator('.auth-diagnostics').screenshot(path=str(ASSETS/'15-auth-diagnostics.png'))
    failed.locator('.steps').screenshot(path=str(ASSETS/'16-stopped-steps.png'))
    print('Captured report, API, evidence and authentication views without report dates.')
    browser.close()
