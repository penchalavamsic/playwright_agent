"""Phase 6 End-to-End Verification Harness.

Verifies:
1. Multi-Account .env & access-profiles.json Credential Management (SUPER_USER, ADMIN).
2. Role-Based Automated Login in BrowserInspector during live inspection.
3. Run 1 (SUPER_USER) -> generates 001_* tagged with SUPER_USER, zero hardcoded passwords/URLs.
4. Run 2 (ADMIN) -> generates 002_* tagged with ADMIN, appends to Test_Plan_IEEE829.md, updates .env.
5. Simulated .exe close & reopen -> reloads workspace state, restores URL/roles/sequence, Run 3 -> 003_*.
6. Intent parser auto-detection of role mentions in user_flow_text ("as super user...").
"""

from __future__ import annotations

import http.server
import json
import shutil
import socketserver
import threading
import time
from pathlib import Path
from typing import Tuple

from agents.intent_parser import detect_access_profile_from_flow
from core.workspace_manager import WorkspaceManager
from gui.app_window import EnterpriseQAStudioApp

OUTPUT_DIR = Path("./sample_output_phase6").resolve()


class _AuthPortalHandler(http.server.BaseHTTPRequestHandler):
    """100% offline fixture portal with login form + authenticated dashboard + search API."""

    def log_message(self, format: str, *args) -> None:
        pass

    def do_GET(self) -> None:
        if self.path.startswith("/api/search"):
            payload = json.dumps({"status": "ok", "results": ["item1", "item2"]}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        if self.path.startswith("/dashboard"):
            html = """<!DOCTYPE html>
<html>
<head><title>Enterprise Portal - Dashboard</title></head>
<body>
  <h1>Enterprise Dashboard</h1>
  <div role="tab" aria-label="Dashboard">Dashboard</div>
  <input id="search-box" type="search" placeholder="Search records..." />
  <button id="search-btn" type="button" onclick="fetch('/api/search?q=' + document.getElementById('search-box').value)">Search</button>
</body>
</html>""".encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
            return

        # Default: Login page
        html = """<!DOCTYPE html>
<html>
<head><title>Enterprise Portal - Login</title></head>
<body>
  <h1>Sign In</h1>
  <form method="GET" action="/dashboard">
    <label for="username">Username</label>
    <input id="username" name="username" type="text" placeholder="Enter username" />
    <label for="password">Password</label>
    <input id="password" name="password" type="password" placeholder="Enter password" />
    <button type="submit">Log in</button>
  </form>
</body>
</html>""".encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)


def start_auth_fixture_server() -> Tuple[http.server.ThreadingHTTPServer, str]:
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _AuthPortalHandler)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server, f"http://127.0.0.1:{port}"


def _run_gui_pipeline_and_wait(app: EnterpriseQAStudioApp, timeout_s: float = 45.0) -> None:
    app._on_start_clicked()
    start = time.time()
    while app._is_running and (time.time() - start) < timeout_s:
        app.update()
        time.sleep(0.05)
    app.update()
    if app._is_running:
        print("  [DEBUG] Console output on timeout:\n" + app.console_textbox.get("0.0", "end"))


def test_phase6_e2e() -> int:
    print("=" * 80)
    print("PHASE 6 END-TO-END VERIFICATION: MULTI-ACCOUNT .ENV & MULTI-DAY WORKSPACE")
    print("=" * 80)

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    server, local_url = start_auth_fixture_server()
    print(f"Offline Auth Fixture Portal: {local_url}")

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

    # Unit check: intent parser role detection
    check(
        detect_access_profile_from_flow("as super user verify dashboard search", "ADMIN") == "SUPER_USER",
        "Intent parser detects 'as super user' and overrides to SUPER_USER",
    )
    check(
        detect_access_profile_from_flow("login as admin and check reports", "SUPER_USER") == "ADMIN",
        "Intent parser detects 'login as admin' and overrides to ADMIN",
    )

    app = EnterpriseQAStudioApp(is_test_mode=True)
    app.withdraw()

    try:
        # Configure Output Dir & URL
        app.out_entry.delete(0, "end")
        app.out_entry.insert(0, str(OUTPUT_DIR))
        app.url_entry.delete(0, "end")
        app.url_entry.insert(0, local_url)

        # 1. Save multiple role accounts via GUI Vault
        app.role_combo.set("SUPER_USER")
        app.username_entry.delete(0, "end")
        app.username_entry.insert(0, "super_qa@corp.local")
        app.password_entry.delete(0, "end")
        app.password_entry.insert(0, "SuperSecret#123")
        app._on_save_role_account()

        app.role_combo.set("ADMIN")
        app.username_entry.delete(0, "end")
        app.username_entry.insert(0, "admin_qa@corp.local")
        app.password_entry.delete(0, "end")
        app.password_entry.insert(0, "AdminSecret#456")
        app._on_save_role_account()

        check(
            "SUPER_USER" in app.saved_roles_lbl.cget("text") and "ADMIN" in app.saved_roles_lbl.cget("text"),
            "GUI Saved Roles indicator lists SUPER_USER and ADMIN",
        )
        check(app.seq_badge_lbl.cget("text") == "Next Test ID: 001", "Initial Next Test ID badge is 001")

        # ------------------------------------------------------------------
        # RUN 1: Execute as SUPER_USER
        # ------------------------------------------------------------------
        print("\n--- Run 1: Executing as SUPER_USER ---")
        app.profile_dropdown.set("SUPER_USER")
        app.flow_text.delete("0.0", "end")
        app.flow_text.insert("0.0", "Search dashboard records and verify 200 status code")
        _run_gui_pipeline_and_wait(app)

        check(not app._is_running, "Run 1 completed within timeout")
        env_text_1 = (OUTPUT_DIR / ".env").read_text(encoding="utf-8")
        check("TEST_ACCESS_PROFILE=SUPER_USER" in env_text_1, "Run 1 .env sets TEST_ACCESS_PROFILE=SUPER_USER")
        check("SUPER_USER_USERNAME=super_qa@corp.local" in env_text_1, ".env contains SUPER_USER_USERNAME")
        check("ADMIN_USERNAME=admin_qa@corp.local" in env_text_1, ".env contains ADMIN_USERNAME")
        check((OUTPUT_DIR / "access-profiles.json").exists(), "access-profiles.json generated")
        check((OUTPUT_DIR / ".env.example").exists(), ".env.example generated")
        check(
            "SuperSecret#123" not in (OUTPUT_DIR / ".env.example").read_text(encoding="utf-8"),
            ".env.example contains zero real passwords",
        )
        gitignore_text = (OUTPUT_DIR / ".gitignore").read_text(encoding="utf-8")
        check(".env" in gitignore_text and ".qa_studio_project.json" in gitignore_text, ".gitignore ignores .env and .qa_studio_project.json")

        py_tests_dir = OUTPUT_DIR / "Python_Playwright" / "tests"
        run1_py = list(py_tests_dir.glob("001_*.py"))
        check(len(run1_py) == 1, f"Run 1 generated 001_*.py ({run1_py[0].name if run1_py else 'none'})")
        if run1_py:
            py_code = run1_py[0].read_text(encoding="utf-8")
            check("SuperSecret#123" not in py_code and "super_qa@corp.local" not in py_code, "Run 1 script has zero hardcoded credentials")
            check("login_with_profile" in py_code and "TEST_ACCESS_PROFILE" in py_code, "Run 1 script calls login_with_profile(os.getenv('TEST_ACCESS_PROFILE', ...))")
            check(local_url not in py_code, "Run 1 script has zero hardcoded URLs")

        plan_text_1 = (OUTPUT_DIR / "docs" / "Test_Plan_IEEE829.md").read_text(encoding="utf-8")
        check('access_profile: "SUPER_USER"' in plan_text_1, "Run 1 Test Plan frontmatter has access_profile: SUPER_USER")
        check("${TEST_ACCESS_PROFILE}" in plan_text_1, "Run 1 Test Plan Preconditions references ${TEST_ACCESS_PROFILE}")
        check(app.seq_badge_lbl.cget("text") == "Next Test ID: 002", "GUI Next Test ID badge updated to 002 after Run 1")

        # ------------------------------------------------------------------
        # RUN 2: Switch dropdown to ADMIN
        # ------------------------------------------------------------------
        print("\n--- Run 2: Switching Dropdown to ADMIN ---")
        app.profile_dropdown.set("ADMIN")
        app.flow_text.delete("0.0", "end")
        app.flow_text.insert("0.0", "Verify dashboard tab and search API 200")
        _run_gui_pipeline_and_wait(app)

        check(not app._is_running, "Run 2 completed within timeout")
        env_text_2 = (OUTPUT_DIR / ".env").read_text(encoding="utf-8")
        check("TEST_ACCESS_PROFILE=ADMIN" in env_text_2, "Run 2 .env updated to TEST_ACCESS_PROFILE=ADMIN")

        run1_py_after = list(py_tests_dir.glob("001_*.py"))
        run2_py = list(py_tests_dir.glob("002_*.py"))
        check(len(run1_py_after) == 1 and len(run2_py) == 1, "Run 2 created 002_*.py without overwriting 001_*.py")

        plan_text_2 = (OUTPUT_DIR / "docs" / "Test_Plan_IEEE829.md").read_text(encoding="utf-8")
        check('access_profile: "SUPER_USER"' in plan_text_2 and 'access_profile: "ADMIN"' in plan_text_2, "Test_Plan_IEEE829.md appended Run 002 (ADMIN) while preserving Run 001 (SUPER_USER)")
        check(app.seq_badge_lbl.cget("text") == "Next Test ID: 003", "GUI Next Test ID badge updated to 003 after Run 2")

    finally:
        app.destroy()

    # ------------------------------------------------------------------
    # RUN 3: Simulate closing and reopening .exe
    # ------------------------------------------------------------------
    print("\n--- Run 3: Simulating .exe Restart & Open Existing Project ---")
    app2 = EnterpriseQAStudioApp(is_test_mode=True)
    app2.withdraw()
    try:
        app2.load_workspace(OUTPUT_DIR)
        check(app2.url_entry.get().strip() == local_url, "Reopened app restored Target URL from .qa_studio_project.json")
        check(app2.seq_badge_lbl.cget("text") == "Next Test ID: 003", "Reopened app restored Next Test ID: 003")
        check("SUPER_USER" in app2.saved_roles_lbl.cget("text") and "ADMIN" in app2.saved_roles_lbl.cget("text"), "Reopened app restored saved role accounts")

        # Flow prompt explicitly says "as super user" -> intent_parser auto-selects SUPER_USER
        app2.profile_dropdown.set("ADMIN")
        app2.flow_text.delete("0.0", "end")
        app2.flow_text.insert("0.0", "As super user search records and verify 200 status")
        _run_gui_pipeline_and_wait(app2)

        check(not app2._is_running, "Run 3 completed within timeout")
        py_tests_dir = OUTPUT_DIR / "Python_Playwright" / "tests"
        run3_py = list(py_tests_dir.glob("003_*.py"))
        check(len(run3_py) == 1, f"Run 3 created 003_*.py ({run3_py[0].name if run3_py else 'none'})")
        check(len(list(py_tests_dir.glob("001_*.py"))) == 1 and len(list(py_tests_dir.glob("002_*.py"))) == 1, "001_* and 002_* preserved after Run 3")

        env_text_3 = (OUTPUT_DIR / ".env").read_text(encoding="utf-8")
        check("TEST_ACCESS_PROFILE=SUPER_USER" in env_text_3, "Run 3 auto-detected 'as super user' from prompt and updated .env to SUPER_USER")

        proj_json = json.loads((OUTPUT_DIR / ".qa_studio_project.json").read_text(encoding="utf-8"))
        check(proj_json.get("last_sequence_number") == 3, ".qa_studio_project.json last_sequence_number is 3")
        check(len(proj_json.get("history", [])) == 3, ".qa_studio_project.json recorded 3 runs in history")
        check("SuperSecret#123" not in json.dumps(proj_json), ".qa_studio_project.json stores base64 password_b64, not plaintext")

    finally:
        app2.destroy()
        server.shutdown()

    print("\n" + "=" * 80)
    print(f"PHASE 6 VERIFICATION RESULT: {passed} PASSED, {failed} FAILED")
    print("=" * 80)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(test_phase6_e2e())
