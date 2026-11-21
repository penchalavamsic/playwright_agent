"""Pytest configuration, corporate Playwright browser fixtures, and Enterprise Report hooks."""

import datetime
import html
import json
import os
from pathlib import Path
from typing import Any, Dict, List
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Page, Playwright


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=True)
_COLLECTED_RESULTS: List[Dict[str, Any]] = []


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", "")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    video_dir = Path("test-results") / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    return {
        **browser_context_args,
        "ignore_https_errors": True,
        "viewport": {"width": 1280, "height": 720},
        "record_video_dir": str(video_dir.resolve()),
        "record_video_size": {"width": 1280, "height": 720},
    }


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Collect per-test execution status, duration, real screenshots, and video paths."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when != "call":
        return

    test_id = f"PY-{len(_COLLECTED_RESULTS) + 1:03d}"
    report_root = _PROJECT_ROOT / "Complete-Suite-Test-Report"
    ss_dir = report_root / "Evidence" / "Screenshots" / test_id
    ss_dir.mkdir(parents=True, exist_ok=True)
    final_ss_rel = f"Evidence/Screenshots/{test_id}/final-screenshot.png"
    video_rel = f"Evidence/Recording/{test_id}/video.webm"

    page = item.funcargs.get("page") if hasattr(item, "funcargs") else None
    raw_video_path = ""
    if page is not None:
        try:
            page.screenshot(path=str(ss_dir / "final-screenshot.png"), full_page=False)
        except Exception:
            pass
        try:
            if page.video:
                raw_video_path = str(page.video.path())
        except Exception:
            pass

    _COLLECTED_RESULTS.append(
        {
            "test_id": test_id,
            "title": (item.obj.__doc__ or item.name).strip(),
            "status": "passed" if rep.passed else ("failed" if rep.failed else "skipped"),
            "duration_s": round(float(rep.duration), 2),
            "profile": os.getenv("TEST_ACCESS_PROFILE", "ADMIN"),
            "spec_path": str(item.fspath),
            "final_screenshot": final_ss_rel,
            "video_rel_path": video_rel,
            "raw_video_path": raw_video_path,
            "error_message": str(rep.longrepr) if rep.failed else "",
        }
    )


def pytest_sessionfinish(session, exitstatus):
    """Copy finalized .webm videos and write self-contained Complete-Suite-Test-Report/index.html."""
    import shutil

    report_root = _PROJECT_ROOT / "Complete-Suite-Test-Report"
    for sub in ("Plans", "Screenshots", "Recording", "Trace"):
        (report_root / "Evidence" / sub).mkdir(parents=True, exist_ok=True)

    video_staging = Path("test-results") / "videos"
    staged_webms = sorted(video_staging.glob("*.webm"), key=lambda p: p.stat().st_mtime) if video_staging.exists() else []
    for idx, tc in enumerate(_COLLECTED_RESULTS):
        rec_dir = report_root / "Evidence" / "Recording" / tc["test_id"]
        rec_dir.mkdir(parents=True, exist_ok=True)
        dest_webm = rec_dir / "video.webm"
        src_str = tc.get("raw_video_path", "")
        if src_str and Path(src_str).exists() and Path(src_str).stat().st_size > 0:
            shutil.copy2(src_str, dest_webm)
        elif idx < len(staged_webms) and staged_webms[idx].stat().st_size > 0:
            shutil.copy2(staged_webms[idx], dest_webm)

    profile = os.getenv("TEST_ACCESS_PROFILE", "ADMIN") or "PUBLIC"
    total = len(_COLLECTED_RESULTS)
    passed = sum(1 for r in _COLLECTED_RESULTS if r["status"] == "passed")
    failed = sum(1 for r in _COLLECTED_RESULTS if r["status"] == "failed")
    skipped = sum(1 for r in _COLLECTED_RESULTS if r["status"] == "skipped")
    duration_s = round(sum(r["duration_s"] for r in _COLLECTED_RESULTS), 2)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    summary = {
        "report_title": f"Shutterstock Detailed Test Evidence Report — shutterstock.com — {profile}",
        "profile": profile,
        "date": date_str,
        "browser": "Chrome",
        "total": total,
        "passed": passed,
        "failed": failed,
        "flaky": 0,
        "skipped": skipped,
        "duration_s": duration_s,
        "test_cases": _COLLECTED_RESULTS,
    }
    (report_root / "report-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


    cards = []
    for i, tc in enumerate(_COLLECTED_RESULTS):
        st = tc["status"]
        ss_rel = tc.get("final_screenshot", "")
        vid_rel = tc.get("video_rel_path", "")
        ss_html = f'<div class="final-ss"><h4>Final Screenshot</h4><img src="{html.escape(ss_rel)}" style="max-width:640px"></div>' if ss_rel else ""
        vid_html = f'<div class="video-container"><h4>Screen Recording</h4><video controls preload="metadata" style="width:100%;max-width:640px"><source src="{html.escape(vid_rel)}" type="video/webm"></video></div>' if vid_rel else ""
        cards.append(
            f'<div class="test-card {st}" id="test-{i}"><div class="test-header" onclick="toggleExpand('test-{i}')">'
            f'<div class="test-card-heading"><span class="test-id-col">{html.escape(tc["test_id"])}</span>'
            f'<span class="test-title-col">{html.escape(tc["title"])}</span></div>'
            f'<span class="test-status {st}">{st.upper()}</span><span class="test-duration">{tc["duration_s"]:.2f}s</span>'
            f'<span class="expand-icon">▼</span></div><div class="test-body">'
            f'<div class="test-meta"><span><strong>Profile:</strong> {html.escape(profile)}</span></div>'
            f'{ss_html}{vid_html}'
            f'<div class="actual-result"><h4>Actual Result</h4><p><strong>Status:</strong> {st}</p></div></div></div>'
        )

    html_doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{html.escape(summary["report_title"])}</title>
<style>
body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f5f5f5; color: #333; margin: 0; }}
.report-header {{ background: #1a1a2e; color: #fff; padding: 24px; }}
.summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 16px; margin-top: 16px; }}
.summary-card {{ background: rgba(255,255,255,0.1); border-radius: 8px; padding: 12px; text-align: center; }}
.summary-card .summary-value {{ font-size: 1.6em; font-weight: bold; }}
.summary-card.passed .summary-value {{ color: #4caf50; }}
.summary-card.failed .summary-value {{ color: #f44336; }}
.container {{ max-width: 1100px; margin: 0 auto; padding: 24px 16px; }}
.test-card {{ background: #fff; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.test-card.passed {{ border-left: 4px solid #4caf50; }}
.test-card.failed {{ border-left: 4px solid #f44336; }}
.test-header {{ display: flex; align-items: center; padding: 12px 16px; cursor: pointer; gap: 12px; }}
.test-card-heading {{ display: grid; grid-template-columns: minmax(150px, auto) 1fr; gap: 16px; flex: 1; }}
.test-body {{ display: none; padding: 0 16px 16px; }}
.test-card.expanded .test-body {{ display: block; }}
</style></head><body>
<div class="report-header"><h1>{html.escape(summary["report_title"])}</h1>
<div class="summary-grid">
<div class="summary-card"><div class="summary-value">{total}</div><div class="summary-label">Total</div></div>
<div class="summary-card passed"><div class="summary-value">{passed}</div><div class="summary-label">Passed</div></div>
<div class="summary-card failed"><div class="summary-value">{failed}</div><div class="summary-label">Failed</div></div>
<div class="summary-card"><div class="summary-value">{skipped}</div><div class="summary-label">Skipped</div></div>
<div class="summary-card"><div class="summary-value">{duration_s:.2f}s</div><div class="summary-label">Duration</div></div>
<div class="summary-card profile"><div class="summary-value">{html.escape(profile)}</div><div class="summary-label">Profile</div></div>
</div></div><div class="container">{"".join(cards)}</div>
<script>function toggleExpand(id){{document.getElementById(id).classList.toggle('expanded');}}</script></body></html>"""
    (report_root / "index.html").write_text(html_doc, encoding="utf-8")
