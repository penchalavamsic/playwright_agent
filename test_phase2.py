"""Phase 2 end-to-end verification CLI script.

Executes the complete StateGraph pipeline:
START -> intent_parser -> browser_inspector -> test_planner -> END

Verifies:
1. Progress callbacks transition cleanly across all milestones (15% to 75%).
2. ./sample_output/docs/Test_Plan_IEEE829.md is generated with locator tables, API matrix, and test scenarios.
3. ./sample_output/docs/network_har_summary.json is created.
4. Structured TestScenarioSpec objects are created.
"""

from __future__ import annotations

import asyncio
import json
import os
import shutil
import sys
from pathlib import Path

from agents.state import AgentState
from agents.workflow_graph import run_agent_pipeline
from test_phase1 import start_fixture_server

OUTPUT_DIR = Path("./sample_output").resolve()
FLOW_PROMPT = "Create automation script for the dashboard, search API, click button and verify whether it succeeded with 200 or 201 status code"
TARGET_LANGS = ["Python", "Java", "TypeScript", "JavaScript"]

observed_progress = []


def progress_tracker(node_name: str, percent: float, message: str) -> None:
    observed_progress.append((node_name, percent, message))
    pct_val = percent * 100 if percent <= 1.0 else percent
    filled = int(pct_val / 2.5)
    bar = "=" * filled + "-" * (40 - filled)
    print(f"  [{bar}] {pct_val:5.1f}%  {node_name:<30} {message}", flush=True)


async def main() -> int:
    print("=" * 80)
    print("PHASE 2 ZERO-API LANGGRAPH & IEEE 829 TEST PLAN GENERATOR VERIFICATION")
    print("=" * 80)

    # Clean existing sample output
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    # Start offline fixture server (guarantees 100% offline deterministic test)
    server, local_url = start_fixture_server()
    print(f"Offline Fixture Portal launched at: {local_url}")
    print(f"User Flow Prompt: '{FLOW_PROMPT}'\n")

    initial_state: AgentState = {
        "target_url": local_url,
        "user_flow_text": FLOW_PROMPT,
        "target_languages": TARGET_LANGS,
        "output_dir": str(OUTPUT_DIR),
        "headless": True,
        "generate_test_plan": True,
        "generate_scripts": False,
        "progress_callback": progress_tracker,
        "parsed_flow_steps": [],
        "inspection_report": {},
        "test_plan_markdown": "",
        "test_scenarios": [],
        "generated_files": [],
        "errors": [],
    }

    try:
        final_state = await run_agent_pipeline(initial_state)
    finally:
        server.shutdown()

    print("\n" + "=" * 80)
    print("VERIFICATION CHECKS")
    print("=" * 80)

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

    # 1. State integrity
    check(bool(final_state.get("parsed_flow_steps")), f"Parsed flow steps generated ({len(final_state.get('parsed_flow_steps', []))} steps)")
    check(bool(final_state.get("inspection_report")), "Inspection report populated by browser_inspector node")
    check(bool(final_state.get("test_plan_markdown")), f"Test plan markdown generated ({len(final_state.get('test_plan_markdown', ''))} characters)")
    check(len(final_state.get("test_scenarios", [])) >= 3, f"Structured Test Scenarios created ({len(final_state.get('test_scenarios', []))} scenarios)")

    # 2. Progress Milestones
    pct_values = [p[1] for p in observed_progress]
    check(any(0.14 <= p <= 0.16 for p in pct_values), "Milestone 15% (IntentParserNode) reported")
    check(any(0.20 <= p <= 0.55 for p in pct_values), "Milestones 20%-55% (BrowserInspector) reported")
    check(any(0.64 <= p <= 0.66 for p in pct_values), "Milestone 65% (TestPlannerNode) reported")
    check(any(0.74 <= p <= 0.76 for p in pct_values), "Milestone 75% (TestPlannerNode completion) reported")

    # 3. Output files verification
    plan_file = OUTPUT_DIR / "docs" / "Test_Plan_IEEE829.md"
    har_file = OUTPUT_DIR / "docs" / "network_har_summary.json"

    check(plan_file.exists(), f"Test_Plan_IEEE829.md exists at {plan_file}")
    check(har_file.exists(), f"network_har_summary.json exists at {har_file}")

    if plan_file.exists():
        content = plan_file.read_text(encoding="utf-8")
        check("# IEEE 829 CORPORATE TEST PLAN" in content, "Document contains IEEE 829 standard header")
        check("## 3. UI Component & Multi-Language Locator Inventory" in content, "Document contains Multi-Language Locator Inventory")
        check("## 4. Captured Network API & Status Code Verification Matrix" in content, "Document contains Network API Verification Matrix")
        check("## 5. Detailed Test Scenarios & Execution Steps" in content, "Document contains Detailed Test Scenarios section")
        check("page.get_by_test_id" in content or "page.locator" in content, "Document includes exact Playwright locator code")
        check("200" in content and "201" in content, "Document includes status code assertions (200, 201)")

    if har_file.exists():
        har_data = json.loads(har_file.read_text(encoding="utf-8"))
        check(isinstance(har_data, list) and len(har_data) > 0, f"network_har_summary.json contains {len(har_data)} captured API records")

    print("\n" + "=" * 80)
    print(f"PHASE 2 RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    if failed > 0:
        return 1

    print("PHASE 2 TEST PLAN GENERATOR VERIFICATION PASSED SUCCESSFULLY")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

