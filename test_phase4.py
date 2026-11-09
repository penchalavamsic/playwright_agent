"""Phase 4 Automated GUI Verification Harness.

Instantiates EnterpriseQAStudioApp, executes a real pipeline run via the
thread-safe queue mechanism against the offline fixture portal, asserts widget
states, node badges, progress bar, and tab contents, then closes cleanly.
"""

from __future__ import annotations

import os
import shutil
import sys
import time
from pathlib import Path

from gui.app_window import EnterpriseQAStudioApp
from test_phase1 import start_fixture_server

OUTPUT_DIR = Path("./sample_output_gui_phase4").resolve()


def test_gui_automated() -> int:
    print("=" * 80)
    print("PHASE 4 ENTERPRISE QA STUDIO DESKTOP GUI AUTOMATED VERIFICATION")
    print("=" * 80)

    # Clean previous output
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    # 1. Start offline fixture web portal
    server, local_url = start_fixture_server()
    print(f"Offline Fixture Portal: {local_url}")

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

    # 2. Instantiate GUI in test mode (suppresses modal dialogs)
    app = EnterpriseQAStudioApp(is_test_mode=True)
    # Don't show window on screen during headless test run
    app.withdraw()

    try:
        # Check initial widget state
        check(app.title() == "Playwright Enterprise QA Agent Studio (Zero-API Offline Edition)", "Window title initialized correctly")
        check(len(app.node_cards) == 5, "5 Visual LangGraph pipeline cards initialized")
        check(all(card["state"] == "pending" for card in app.node_cards.values()), "All 5 node badges start in 'pending' state")
        check(app.progress_bar.get() == 0.0, "Progress bar starts at 0.0")

        # Configure GUI inputs for test run
        app.url_entry.delete(0, "end")
        app.url_entry.insert(0, local_url)
        app.out_entry.delete(0, "end")
        app.out_entry.insert(0, str(OUTPUT_DIR))

        print("\nTriggering pipeline execution via GUI Start Button...")
        app._on_start_clicked()

        # Poll the Tkinter loop until pipeline finishes
        start_time = time.time()
        timeout_seconds = 30.0

        while app._is_running:
            app.update_idletasks()
            app.update()
            time.sleep(0.05)
            if time.time() - start_time > timeout_seconds:
                check(False, "Execution timed out waiting for pipeline completion")
                break

        # Additional pump to flush completion messages
        for _ in range(10):
            app.update_idletasks()
            app.update()
            time.sleep(0.05)

        print("\nVerifying Post-Execution GUI Widget States:")

        # 3. Verify Progress & Badges
        check(app.progress_bar.get() >= 0.99, f"Progress bar reached 100% (value: {app.progress_bar.get():.2f})")
        check(app.pct_display_lbl.cget("text") == "100%", "Percentage label displays '100%'")
        check(
            all(card["state"] == "completed" for card in app.node_cards.values()),
            "All 5 node badges transitioned to 'completed' state",
        )

        # 4. Verify Telemetry Counters
        dom_text = app.counter_dom_lbl.cget("text")
        api_text = app.counter_api_lbl.cget("text")
        files_text = app.counter_files_lbl.cget("text")

        check("DOM Locators:" in dom_text and not dom_text.endswith(" 0"), f"DOM locator counter updated: {dom_text}")
        check("APIs Intercepted:" in api_text and not api_text.endswith(" 0"), f"API intercepted counter updated: {api_text}")
        check("Files Generated:" in files_text and not files_text.endswith(" 0"), f"Files generated counter updated: {files_text}")

        # 5. Verify Tab 1 (Console Output)
        console_content = app.console_textbox.get("0.0", "end")
        check("[PIPELINE SUCCESS]" in console_content, "Console log captured pipeline success event")
        check("IntentParserNode" in console_content and "BrowserInspector" in console_content, "Console log contains node telemetry")

        # 6. Verify Tab 2 (Test Plan IEEE 829 Markdown)
        plan_content = app.plan_textbox.get("0.0", "end")
        check("# IEEE 829 CORPORATE TEST PLAN" in plan_content, "Tab 2 contains IEEE 829 Corporate Test Plan")
        check("UI Component & Multi-Language Locator Inventory" in plan_content, "Tab 2 contains locator inventory")

        # 7. Verify Tab 3 (Generated Files Previewer)
        check(len(app._generated_files_map) >= 15, f"Tab 3 file selector populated with {len(app._generated_files_map)} files")
        preview_content = app.code_preview_textbox.get("0.0", "end")
        check(len(preview_content.strip()) > 50, "Tab 3 code previewer displays file content")

        # 8. Verify Open Folder Button state
        check(app.open_folder_btn.cget("state") == "normal", "Open Folder button enabled after completion")

    finally:
        # Clean shutdown
        app.destroy()
        server.shutdown()

    print("\n" + "=" * 80)
    print(f"PHASE 4 GUI RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    if failed > 0:
        return 1

    print("PHASE 4 DESKTOP GUI VERIFICATION PASSED SUCCESSFULLY")
    return 0


if __name__ == "__main__":
    sys.exit(test_gui_automated())

