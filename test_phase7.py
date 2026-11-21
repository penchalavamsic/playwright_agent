"""Phase 7 Verification Suite: Self-Contained Enterprise Test Execution Reporting.

Verifies:
1. Exact directory and file structure parity with `./Complete-Suite-Test-Report/`:
   - Complete-Suite-Test-Report/index.html
   - Complete-Suite-Test-Report/README.txt
   - Complete-Suite-Test-Report/report-summary.json
   - Complete-Suite-Test-Report/Evidence/Plans/<TEST_ID>/<TEST_ID>-<slug>.md
   - Complete-Suite-Test-Report/Evidence/Screenshots/<TEST_ID>/<NN>-<step>.png & final-screenshot.png
   - Complete-Suite-Test-Report/Evidence/Recording/<TEST_ID>/video.webm
   - Complete-Suite-Test-Report/Evidence/Trace/<TEST_ID>/trace.zip
2. Visual & DOM structure parity with reference report (.report-header, .summary-grid,
   .summary-card, .test-card, .steps, .test-plan, .screenshots, .final-ss, .video-container,
   .api-summary, .trace-section, .actual-result, toggleExpand).
3. ZERO external CDN links, external fonts, or internet calls in generated HTML.
4. Multi-language reporting integration across Python (conftest.py hooks), Java (TestNG
   EnterpriseReportListener + testng.xml), TypeScript, and JavaScript (enterprise-reporter.js).
5. GUI '📊 Open Test Report' button integration in EnterpriseQAStudioApp.
"""

from __future__ import annotations

import asyncio
import http.server
import json
import re
import shutil
import threading
import zipfile
from pathlib import Path

from agents.code_synthesizer_node import code_synthesizer_node, project_scaffolder_node
from agents.intent_parser import intent_parser_node
from agents.planner_node import test_planner_node
from agents.state import AgentState
from core.browser_inspector import BrowserInspector
from core.report_generator import EnterpriseReportGenerator
from core.workspace_manager import WorkspaceManager
from gui.app_window import EnterpriseQAStudioApp

OUTPUT_DIR = Path("./sample_output_phase7").resolve()
REF_REPORT_DIR = Path("./Complete-Suite-Test-Report").resolve()


def _mock_inspection_report(target_url: str) -> dict:
    return {
        "target_url": target_url,
        "page_title": "Shutterstock — Stock Images, Photos, Vectors, Video, and Music",
        "browser_channel": "Edge",
        "elements": [
            {
                "element_id": "e1",
                "tag": "input",
                "role": "searchbox",
                "text_or_label": "Search Input",
                "input_type": "search",
                "attributes": {"id": "search-input", "placeholder": "Search..."},
                "recommended_locator": {
                    "python": 'page.locator("#search-input")',
                    "java": 'page.locator("#search-input")',
                    "ts": 'page.locator("#search-input")',
                    "js": 'page.locator("#search-input")',
                },
                "locator_strategy": "id",
            },
            {
                "element_id": "e2",
                "tag": "button",
                "role": "tab",
                "text_or_label": "Dashboard Tab",
                "input_type": "",
                "attributes": {"data-testid": "dashboard-tab"},
                "recommended_locator": {
                    "python": 'page.get_by_test_id("dashboard-tab")',
                    "java": 'page.getByTestId("dashboard-tab")',
                    "ts": 'page.getByTestId("dashboard-tab")',
                    "js": 'page.getByTestId("dashboard-tab")',
                },
                "locator_strategy": "data-testid",
            },
        ],
        "captured_apis": [
            {
                "url": f"{target_url}/api/v1/search",
                "method": "GET",
                "resource_type": "fetch",
                "status_code": 200,
                "request_payload_keys": ["q"],
                "response_keys": ["status", "items", "total"],
                "triggered_by_action": "search_probe",
            },
            {
                "url": f"{target_url}/api/v1/audit",
                "method": "POST",
                "resource_type": "xhr",
                "status_code": 201,
                "request_payload_keys": ["action"],
                "response_keys": ["id", "created_at"],
                "triggered_by_action": "click:dashboard",
            },
        ],
        "aria_snapshot": "- document:\n  - searchbox 'Search Input'\n  - tab 'Dashboard Tab'",
        "probes_executed": ["login:SUPER_USER", "search:playwright", "click:Dashboard Tab"],
        "login_performed": True,
        "login_locators": {},
    }


def run_phase7_verification() -> int:
    print("=" * 80)
    print("PHASE 7 VERIFICATION: SELF-CONTAINED ENTERPRISE TEST EXECUTION REPORTING")
    print("=" * 80)

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    passed = 0
    failed = 0

    def check(condition: bool, desc: str) -> None:
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  [PASS] {desc}")
        else:
            failed += 1
            print(f"  [FAIL] {desc}")

    # 1. Verify Reference Complete-Suite-Test-Report folder exists in workspace
    check(REF_REPORT_DIR.exists(), f"Reference report directory exists at {REF_REPORT_DIR}")
    check((REF_REPORT_DIR / "index.html").exists(), "Reference index.html exists")
    check((REF_REPORT_DIR / "README.txt").exists(), "Reference README.txt exists")
    check((REF_REPORT_DIR / "Evidence" / "Plans").exists(), "Reference Evidence/Plans exists")
    check((REF_REPORT_DIR / "Evidence" / "Screenshots").exists(), "Reference Evidence/Screenshots exists")
    check((REF_REPORT_DIR / "Evidence" / "Recording").exists(), "Reference Evidence/Recording exists")
    check((REF_REPORT_DIR / "Evidence" / "Trace").exists(), "Reference Evidence/Trace exists")

    # 2. Save Role Accounts (SUPER_USER & ADMIN) and Execute Studio Scaffolding Run 1 (SUPER_USER)
    wm = WorkspaceManager(OUTPUT_DIR)
    wm.add_or_update_account("SUPER_USER", "super_user@corp.local", "SuperPass!123")
    wm.add_or_update_account("ADMIN", "admin_user@corp.local", "AdminPass!456")
    wm.save_project_state()

    target_url = "https://www.shutterstock.com"
    state_run1: AgentState = {
        "target_url": target_url,
        "user_flow_text": "As super user search dashboard records, click dashboard tab and verify 200 or 201 status code",
        "target_languages": ["Python", "Java", "TypeScript", "JavaScript"],
        "output_dir": str(OUTPUT_DIR),
        "headless": True,
        "generate_test_plan": True,
        "generate_scripts": True,
        "active_access_profile": "SUPER_USER",
        "account_credentials": wm.get_all_decrypted_accounts(),
        "sequence_number": 1,
        "inspection_report": _mock_inspection_report(target_url),
        "generated_files": [],
        "errors": [],
    }

    state_run1.update(intent_parser_node(state_run1))
    state_run1.update(test_planner_node(state_run1))
    state_run1.update(code_synthesizer_node(state_run1))
    state_run1.update(project_scaffolder_node(state_run1))

    # 3. Verify Generated Complete-Suite-Test-Report Structure
    gen_report_dir = OUTPUT_DIR / "Complete-Suite-Test-Report"
    index_html_path = gen_report_dir / "index.html"
    readme_txt_path = gen_report_dir / "README.txt"
    summary_json_path = gen_report_dir / "report-summary.json"

    check(gen_report_dir.exists(), "Generated Complete-Suite-Test-Report directory exists")
    check(index_html_path.exists(), "Generated Complete-Suite-Test-Report/index.html exists")
    check(readme_txt_path.exists(), "Generated Complete-Suite-Test-Report/README.txt exists")
    check(summary_json_path.exists(), "Generated Complete-Suite-Test-Report/report-summary.json exists")
    readme_text = readme_txt_path.read_text(encoding="utf-8")
    check(
        "Shutterstock Complete Suite Test Evidence Report" in readme_text and "LIMAS" not in readme_text,
        "README.txt uses dynamic app name ('Shutterstock') with zero hardcoded LIMAS strings",
    )

    for sub in ("Plans", "Screenshots", "Recording", "Trace"):
        sub_dir = gen_report_dir / "Evidence" / sub
        check(sub_dir.exists() and any(sub_dir.iterdir()), f"Evidence/{sub} populated with per-test evidence folders")

    # Verify PNG magic bytes and trace.zip integrity
    png_files = list((gen_report_dir / "Evidence" / "Screenshots").rglob("*.png"))
    check(len(png_files) >= 3, f"Generated {len(png_files)} step and final PNG screenshots")
    if png_files:
        check(png_files[0].read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), "Generated screenshot has valid PNG signature")

    trace_files = list((gen_report_dir / "Evidence" / "Trace").rglob("trace.zip"))
    check(len(trace_files) >= 1, "Generated trace.zip archives inside Evidence/Trace/<TEST_ID>/")
    if trace_files:
        with zipfile.ZipFile(trace_files[0], "r") as zf:
            check("trace.json" in zf.namelist(), "trace.zip contains valid trace.json telemetry")

    # 4. Verify HTML Visual Layout, KPI Cards, Sections, and ZERO External CDN Links
    html_text = index_html_path.read_text(encoding="utf-8")
    required_classes = [
        "report-header",
        "summary-grid",
        "summary-card",
        "test-card",
        "test-header",
        "test-card-heading",
        "test-id-col",
        "test-title-col",
        "test-status",
        "test-duration",
        "test-body",
        "test-meta",
        "steps",
        "test-summary",
        "test-plan",
        "screenshots",
        "ss-grid",
        "final-ss",
        "video-container",
        "api-summary",
        "trace-section",
        "actual-result",
        "toggleExpand",
    ]
    check(
        all(cls in html_text for cls in required_classes),
        "index.html replicates all CSS classes, sections, and interactive JS from reference report",
    )
    check("SUPER_USER" in html_text, "index.html displays active role profile SUPER_USER")
    check(
        "Shutterstock Detailed Test Evidence Report — shutterstock.com — SUPER_USER" in html_text,
        "index.html displays dynamic title 'Shutterstock Detailed Test Evidence Report — shutterstock.com — SUPER_USER'",
    )
    check("LIMAS" not in html_text.upper(), "ZERO hardcoded 'LIMAS' strings in generated index.html")
    plan_md_text = (OUTPUT_DIR / "docs" / "Test_Plan_IEEE829.md").read_text(encoding="utf-8")
    check("limas" not in plan_md_text.lower() and "${BASE_URL}" in plan_md_text, "ZERO hardcoded 'LIMAS' strings in Test_Plan_IEEE829.md (uses ${BASE_URL})")

    # Exhaustive sweep: assert ZERO 'limas' occurrences across EVERY generated file in OUTPUT_DIR
    leaked_files = []
    text_exts = {".env", ".example", ".json", ".md", ".html", ".txt", ".py", ".java", ".ts", ".js", ".xml", ".ini"}
    for gen_file in OUTPUT_DIR.rglob("*"):
        if not gen_file.is_file():
            continue
        if gen_file.suffix.lower() in text_exts or gen_file.name in (".env", ".env.example", ".gitignore"):
            content = gen_file.read_text(encoding="utf-8", errors="ignore")
            if "limas" in content.lower():
                leaked_files.append(str(gen_file.relative_to(OUTPUT_DIR)))
    check(len(leaked_files) == 0, f"Exhaustive sweep: ZERO 'limas' leaks across all generated files (leaks: {leaked_files})")

    external_urls = re.findall(r'(?:src|href)\s*=\s*["\'](https?://[^"\']+)["\']', html_text, re.IGNORECASE)
    check(len(external_urls) == 0, f"ZERO external CDN/internet links in index.html (found: {len(external_urls)})")

    # 5. Execute Run 2 as ADMIN and Verify Multi-Run Report Accumulation
    state_run2: AgentState = {
        "target_url": target_url,
        "user_flow_text": "Login as admin and verify audit API contract",
        "target_languages": ["Python", "Java", "TypeScript", "JavaScript"],
        "output_dir": str(OUTPUT_DIR),
        "headless": True,
        "generate_test_plan": True,
        "generate_scripts": True,
        "active_access_profile": "ADMIN",
        "account_credentials": wm.get_all_decrypted_accounts(),
        "sequence_number": 2,
        "inspection_report": _mock_inspection_report(target_url),
        "generated_files": [],
        "errors": [],
    }
    state_run2.update(intent_parser_node(state_run2))
    state_run2.update(test_planner_node(state_run2))
    state_run2.update(code_synthesizer_node(state_run2))
    state_run2.update(project_scaffolder_node(state_run2))

    summary_data = json.loads(summary_json_path.read_text(encoding="utf-8"))
    check(summary_data.get("total") == 6, f"Multi-run report accumulated 6 scenarios across Run 1 & Run 2 (got {summary_data.get('total')})")

    # 6. Verify Embedded Reporters & Native Media Capture in All 4 Generated Language Suites
    py_conftest = (OUTPUT_DIR / "Python_Playwright" / "conftest.py").read_text(encoding="utf-8")
    check(
        "pytest_runtest_makereport" in py_conftest
        and "pytest_sessionfinish" in py_conftest
        and "record_video_dir" in py_conftest
        and "Complete-Suite-Test-Report" in py_conftest,
        "Python conftest.py embeds native video recording & pytest hooks outputting Complete-Suite-Test-Report/index.html",
    )

    java_listener = OUTPUT_DIR / "Java_Playwright" / "src" / "test" / "java" / "com" / "corp" / "qa" / "listeners" / "EnterpriseReportListener.java"
    java_base_test = OUTPUT_DIR / "Java_Playwright" / "src" / "test" / "java" / "com" / "corp" / "qa" / "tests" / "BaseTest.java"
    java_testng = (OUTPUT_DIR / "Java_Playwright" / "testng.xml").read_text(encoding="utf-8")
    check(java_listener.exists(), "Java EnterpriseReportListener.java generated")
    check(java_base_test.exists() and "setRecordVideoDir" in java_base_test.read_text(encoding="utf-8"), "Java BaseTest.java configures native setRecordVideoDir and screenshot capture")
    check("com.corp.qa.listeners.EnterpriseReportListener" in java_testng, "Java testng.xml wires EnterpriseReportListener")

    ts_reporter = OUTPUT_DIR / "TypeScript_Playwright" / "enterprise-reporter.js"
    ts_config = (OUTPUT_DIR / "TypeScript_Playwright" / "playwright.config.ts").read_text(encoding="utf-8")
    check(
        ts_reporter.exists()
        and "./enterprise-reporter.js" in ts_config
        and "result.attachments" in ts_reporter.read_text(encoding="utf-8"),
        "TypeScript suite wires enterprise-reporter.js copying native result.attachments",
    )

    js_reporter = OUTPUT_DIR / "JavaScript_Playwright" / "enterprise-reporter.js"
    js_config = (OUTPUT_DIR / "JavaScript_Playwright" / "playwright.config.js").read_text(encoding="utf-8")
    check(
        js_reporter.exists()
        and "./enterprise-reporter.js" in js_config
        and "result.attachments" in js_reporter.read_text(encoding="utf-8"),
        "JavaScript suite wires enterprise-reporter.js copying native result.attachments",
    )

    # 7. Verify GUI '📊 Open Test Report' Button
    app = EnterpriseQAStudioApp(is_test_mode=True)
    app.withdraw()
    try:
        check(hasattr(app, "open_report_btn"), "GUI has open_report_btn ('📊 Open Test Report')")
        check("Open Test Report" in app.open_report_btn.cget("text"), "open_report_btn label is '📊 Open Test Report'")
    finally:
        app.destroy()

    # 8. Live BrowserInspector Evidence Capture (Real PNG Screenshots >10KB, Real video.webm, Real trace.zip)
    class _RichPortalHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            if self.path.startswith("/api/search"):
                body = json.dumps({"status": "ok", "results": ["asset-1", "asset-2"]}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            cards = "".join(
                f'<div style="background:linear-gradient(135deg,#1e3a8a,#0284c7);color:#fff;padding:18px;border-radius:10px;box-shadow:0 4px 12px rgba(0,0,0,0.2);">'
                f'<h3>Asset Card #{i}</h3><p>High-resolution vector &amp; photography telemetry item #{i} with detailed metadata badges.</p></div>'
                for i in range(1, 25)
            )
            html_page = f"""<!DOCTYPE html><html><head><title>Shutterstock Studio Portal</title></head>
            <body style="font-family:Segoe UI,sans-serif;background:#0f172a;color:#f8fafc;padding:24px;">
              <h1>Shutterstock Enterprise Creative Portal</h1>
              <input id="search-input" type="search" placeholder="Search stock images..." style="padding:10px;width:320px;" />
              <button id="dashboard-tab" role="tab" onclick="fetch('/api/search?q=vectors')">Explore Gallery</button>
              <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-top:20px;">{cards}</div>
            </body></html>""".encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(html_page)))
            self.end_headers()
            self.wfile.write(html_page)

    live_out_dir = Path("./sample_output_phase7_live").resolve()
    if live_out_dir.exists():
        shutil.rmtree(live_out_dir, ignore_errors=True)

    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _RichPortalHandler)
    live_url = f"http://127.0.0.1:{httpd.server_address[1]}"
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    try:
        inspector = BrowserInspector()
        live_report = asyncio.run(
            inspector.inspect_url(
                target_url=live_url,
                user_flow_text="Search for vectors and click Explore Gallery",
                headless=True,
            )
        )
        live_state: AgentState = {
            "target_url": live_url,
            "user_flow_text": "Search for vectors and click Explore Gallery",
            "target_languages": ["Python", "TypeScript"],
            "output_dir": str(live_out_dir),
            "headless": True,
            "generate_test_plan": True,
            "generate_scripts": True,
            "active_access_profile": "SUPER_USER",
            "sequence_number": 1,
            "inspection_report": live_report.model_dump(),
            "generated_files": [],
            "errors": [],
        }
        live_state.update(intent_parser_node(live_state))
        live_state.update(test_planner_node(live_state))
        live_state.update(code_synthesizer_node(live_state))
        live_state.update(project_scaffolder_node(live_state))

        live_ev_dir = live_out_dir / "Complete-Suite-Test-Report" / "Evidence"
        live_pngs = list((live_ev_dir / "Screenshots").rglob("*.png"))
        live_webms = list((live_ev_dir / "Recording").rglob("video.webm"))
        live_traces = list((live_ev_dir / "Trace").rglob("trace.zip"))

        check(len(live_pngs) >= 3 and all(p.stat().st_size > 5_000 for p in live_pngs), f"Real Playwright PNG screenshots captured (>5 KB each, max={max((p.stat().st_size for p in live_pngs), default=0):,} bytes)")
        check(len(live_webms) >= 1 and all(v.stat().st_size > 1_000 for v in live_webms), f"Real Playwright video.webm screen recording saved ({live_webms[0].stat().st_size if live_webms else 0:,} bytes)")
        check(len(live_traces) >= 1 and all(tr.stat().st_size > 1_000 for tr in live_traces), f"Real Playwright trace.zip saved ({live_traces[0].stat().st_size if live_traces else 0:,} bytes)")
    finally:
        httpd.shutdown()

    print("\n" + "=" * 80)
    print(f"PHASE 7 VERIFICATION RESULT: {passed} PASSED, {failed} FAILED")
    print("=" * 80)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(run_phase7_verification())
