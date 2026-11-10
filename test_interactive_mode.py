"""Automated test for Interactive Manual Session / Persistent Browser Mode.

Tests the two-step workflow:
Step A: Launch & Keep Browser Open with pause_for_user=True
Step B: Set capture trigger and verify telemetry capture and suite generation.
"""

from __future__ import annotations

import os
import shutil
import sys
import threading
import time
from pathlib import Path

from gui.app_window import EnterpriseQAStudioApp
from test_phase1 import start_fixture_server

OUTPUT_DIR = Path("./sample_output_interactive_test").resolve()


def test_interactive_session_mode() -> int:
    print("=" * 80)
    print("TESTING INTERACTIVE MANUAL SESSION / PERSISTENT BROWSER MODE")
    print("=" * 80)

    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

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

    app = EnterpriseQAStudioApp(is_test_mode=True)
    app.withdraw()

    try:
        # 1. Enable Interactive Mode switch
        app.switch_interactive.select()
        app._on_interactive_toggled()

        check(
            "Step A: Launch & Keep Browser Open" in app.run_btn.cget("text"),
            "Button text updated to 'Step A: Launch & Keep Browser Open'",
        )

        app.url_entry.delete(0, "end")
        app.url_entry.insert(0, local_url)
        app.out_entry.delete(0, "end")
        app.out_entry.insert(0, str(OUTPUT_DIR))

        # 2. Trigger Step A
        print("\nTriggering Step A (Launch & Keep Browser Open)...")
        app._on_start_clicked()

        # Pump GUI until Step B button appears
        step_b_ready = False
        start_time = time.time()
        while time.time() - start_time < 20.0:
            app.update_idletasks()
            app.update()
            time.sleep(0.05)
            # Check if capture_btn is packed/managed in layout
            if app._interactive_trigger_event is not None and (app.capture_btn.winfo_manager() != ""):
                step_b_ready = True
                break

        check(step_b_ready, "Step B 'Capture State & Generate Suite' button displayed to user")
        check(
            app._interactive_trigger_event is not None and not app._interactive_trigger_event.is_set(),
            "Interactive capture trigger event initialized in waiting state",
        )

        # Allow browser to stay persistent for a brief period to simulate user manual interactions
        time.sleep(1.0)
        app.update_idletasks()
        app.update()

        # 3. Trigger Step B
        print("\nTriggering Step B (Capture State & Generate Suite)...")
        app._on_capture_clicked()
        check(app._interactive_trigger_event.is_set(), "Capture trigger event signaled")

        # Wait for pipeline completion
        start_wait = time.time()
        while app._is_running and time.time() - start_wait < 25.0:
            app.update_idletasks()
            app.update()
            time.sleep(0.05)

        for _ in range(10):
            app.update_idletasks()
            app.update()
            time.sleep(0.05)

        # 4. Verify completion states
        check(app.progress_bar.get() >= 0.99, "Progress bar reached 100%")
        check(app.pct_display_lbl.cget("text") == "100%", "Percentage label is 100%")
        check(
            all(card["state"] == "completed" for card in app.node_cards.values()),
            "All 5 node badges completed",
        )
        check(
            (OUTPUT_DIR / "docs" / "Test_Plan_IEEE829.md").exists(),
            "Test_Plan_IEEE829.md generated from interactive session",
        )
        check(
            (OUTPUT_DIR / "Python_Playwright" / "tests" / "test_automation_suite.py").exists(),
            "Python Playwright test suite generated from interactive session",
        )

    finally:
        app.destroy()
        server.shutdown()

    print("\n" + "=" * 80)
    print(f"INTERACTIVE MODE RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(test_interactive_session_mode())

