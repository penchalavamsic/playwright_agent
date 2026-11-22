"""Copied into generated Python projects as conftest.py."""
import hashlib
import json
import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pytest
from dotenv import load_dotenv
from report_renderer import EnterpriseReportGenerator
from auth_session import settings
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT.parent / '.env')
REPORT = ROOT / 'execution-reports' / (datetime.now().strftime('%Y%m%d-%H%M%S') + '-' + uuid4().hex[:8])
RESULTS = {}


def record(item):
    return RESULTS.setdefault(item.nodeid, dict(
        test_id='PY-' + hashlib.sha256(item.nodeid.encode()).hexdigest()[:12],
        title=item.nodeid, status='not_run', duration_s=0.0, error_message='',
        profile=os.getenv('TEST_ACCESS_PROFILE', 'PUBLIC'), spec_path=item.nodeid,
        final_screenshot='', video_rel_path='', trace_rel_path='', captured_apis=[]))


@pytest.fixture(scope='session')
def base_url():
    return os.getenv('BASE_URL', '')


@pytest.fixture(scope='session')
def browser(playwright):
    if settings().get('session_mode') == 'persistent':
        yield None
        return
    errors = []
    channels = [os.getenv('BROWSER_CHANNEL')] if os.getenv('BROWSER_CHANNEL') else ['msedge', 'chrome', None]
    for channel in channels:
        try:
            browser = playwright.chromium.launch(channel=channel, headless=True)
            break
        except Exception as exc:
            errors.append(str(exc))
    else:
        raise RuntimeError('No usable browser. ' + '\n'.join(errors))
    yield browser
    browser.close()


@pytest.fixture
def page(browser, request, playwright, base_url):
    result = record(request.node)
    folder = REPORT / 'Evidence' / result['test_id']
    folder.mkdir(parents=True, exist_ok=True)
    persistent = settings().get('session_mode') == 'persistent'
    marker = request.node.get_closest_marker('qa_profile')
    role = marker.args[0] if marker else os.getenv('TEST_ACCESS_PROFILE', 'PUBLIC')
    channel = os.getenv('BROWSER_CHANNEL', 'msedge')
    parsed = urlsplit(base_url)
    identity = f'{parsed.scheme}://{parsed.netloc}|{role}|{channel}'
    profile = ROOT / '.browser_profiles' / hashlib.sha256(identity.encode()).hexdigest()[:24]
    def open_context(video=True):
        options = dict(ignore_https_errors=True, viewport={'width': 1280, 'height': 720})
        if video:
            options['record_video_dir'] = str(folder / 'raw-video')
        if persistent:
            return playwright.chromium.launch_persistent_context(str(profile), channel=channel, headless=True, **options)
        return browser.new_context(**options)
    try:
        context = open_context()
    except Exception as exc:
        if 'ffmpeg' not in str(exc).lower():
            raise
        context = open_context(False)
    try:
        page = context.pages[0] if context.pages else context.new_page()
    except Exception as exc:
        context.close()
        if 'ffmpeg' not in str(exc).lower():
            raise
        context = open_context(False)
        page = context.new_page()
        result['media_note'] = 'Video unavailable: ffmpeg is not installed.'
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page.on('response', lambda r: result['captured_apis'].append(dict(url=r.url, method=r.request.method, status_code=r.status)) if r.request.resource_type in ('xhr', 'fetch') else None)
    try:
        yield page
    finally:
        result['final_route'] = page.url
        video = page.video
        try:
            page.screenshot(path=str(folder / 'final-screenshot.png'))
            result['final_screenshot'] = (folder / 'final-screenshot.png').relative_to(REPORT).as_posix()
        except Exception as exc:
            result['media_note'] = str(exc)
        try:
            context.tracing.stop(path=str(folder / 'trace.zip'))
            result['trace_rel_path'] = (folder / 'trace.zip').relative_to(REPORT).as_posix()
        finally:
            context.close()
        if video:
            source = Path(video.path())
            if source.is_file() and source.stat().st_size:
                shutil.copy2(source, folder / 'video.webm')
                result['video_rel_path'] = (folder / 'video.webm').relative_to(REPORT).as_posix()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    result = record(item)
    result['duration_s'] += rep.duration
    if rep.failed:
        result['status'] = 'failed'
        result['error_message'] += f'{rep.when}: {rep.longrepr}\n'
    elif rep.skipped and result['status'] != 'failed':
        result['status'] = 'skipped'
        result['error_message'] = str(rep.longrepr)
    elif rep.when == 'call' and result['status'] not in ('failed', 'skipped'):
        result['status'] = 'passed'


def pytest_sessionfinish(session, exitstatus):
    REPORT.mkdir(parents=True, exist_ok=True)
    cases = list(RESULTS.values())
    passed = sum(c['status'] == 'passed' for c in cases)
    failed = sum(c['status'] == 'failed' for c in cases)
    summary = dict(report_title='Python flow execution report', browser=os.getenv('BROWSER_CHANNEL', 'Auto-detected'),
                   date=datetime.now().isoformat(), total=len(cases), passed=passed, failed=failed,
                   skipped=sum(c['status'] == 'skipped' for c in cases), flaky=0,
                   pass_rate_pct=round(100 * passed / (passed + failed), 1) if passed + failed else 0,
                   duration_s=sum(c['duration_s'] for c in cases), test_cases=cases, exit_code=int(exitstatus))
    (REPORT / 'report-summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    (REPORT / 'index.html').write_text(EnterpriseReportGenerator.render_html_report(summary), encoding='utf-8')
    print(f'\nExecution report: {REPORT / "index.html"}')
