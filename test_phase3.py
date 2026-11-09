"""Phase 3 end-to-end verification CLI script.

Executes the complete 5-node StateGraph pipeline:
START -> intent_parser -> browser_inspector -> test_planner -> code_synthesizer -> project_scaffolder -> END

Verifies:
1. Multi-language output generated in:
   - Python_Playwright/
   - Java_Playwright/
   - TypeScript_Playwright/
   - JavaScript_Playwright/
   - docs/Test_Plan_IEEE829.md
   - README.md
2. Python syntax validity via ast.parse and py_compile.compile on all generated Python files.
3. Java, TS, and JS files contain proper classes, locators, and HTTP status code assertions ([200, 201]).
4. Progress milestones reported smoothly up to 100%.
"""

from __future__ import annotations

import ast
import asyncio
import os
import py_compile
import shutil
import sys
from pathlib import Path

from agents.state import AgentState
from agents.workflow_graph import run_agent_pipeline
from test_phase1 import start_fixture_server

OUTPUT_DIR = Path("./sample_output_phase3").resolve()
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
    print("PHASE 3 MULTI-LANGUAGE PLAYWRIGHT CODE SYNTHESIZER & SCAFFOLDER VERIFICATION")
    print("=" * 80)

    # Clean previous run
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    # Launch offline fixture app
    server, local_url = start_fixture_server()
    print(f"Offline Fixture Portal: {local_url}")
    print(f"User Flow Prompt: '{FLOW_PROMPT}'\n")

    initial_state: AgentState = {
        "target_url": local_url,
        "user_flow_text": FLOW_PROMPT,
        "target_languages": TARGET_LANGS,
        "output_dir": str(OUTPUT_DIR),
        "headless": True,
        "generate_test_plan": True,
        "generate_scripts": True,
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

    # 1. Check generated files count
    created_files = final_state.get("generated_files", [])
    check(len(created_files) >= 15, f"All expected corporate files scaffolded (Total: {len(created_files)})")

    # 2. Check Master README & Docs
    readme = OUTPUT_DIR / "README.md"
    check(readme.exists(), f"Master README.md exists at {readme}")
    test_plan = OUTPUT_DIR / "docs" / "Test_Plan_IEEE829.md"
    check(test_plan.exists(), f"Test_Plan_IEEE829.md exists at {test_plan}")

    # 3. Python Verification
    py_dir = OUTPUT_DIR / "Python_Playwright"
    py_base_page = py_dir / "pages" / "base_page.py"
    py_app_page = py_dir / "pages" / "app_page.py"
    py_test_suite = py_dir / "tests" / "test_automation_suite.py"
    py_conftest = py_dir / "conftest.py"
    py_reqs = py_dir / "requirements.txt"

    check(py_base_page.exists() and py_app_page.exists() and py_test_suite.exists() and py_conftest.exists(), "Python Playwright POM suite structure exists")

    # Python AST & Bytecode Syntax Compilation Check
    for p_file in [py_base_page, py_app_page, py_test_suite, py_conftest]:
        if p_file.exists():
            code = p_file.read_text(encoding="utf-8")
            try:
                ast.parse(code)
                py_compile.compile(str(p_file), doraise=True)
                check(True, f"Python syntax valid & compilable: {p_file.name}")
            except Exception as e:
                check(False, f"Python syntax check failed for {p_file.name}: {e}")

    # Verify status code assertions in Python suite
    if py_test_suite.exists():
        py_test_content = py_test_suite.read_text(encoding="utf-8")
        check("200" in py_test_content and "201" in py_test_content, "Python test suite includes status code assertions (200, 201)")
        check("wait_for_api_response" in py_test_content or "expect_response" in py_test_content, "Python test suite includes API response interceptor")

    # 4. Java Verification
    java_dir = OUTPUT_DIR / "Java_Playwright"
    java_pom = java_dir / "pom.xml"
    java_testng = java_dir / "testng.xml"
    java_base_page = java_dir / "src" / "main" / "java" / "com" / "corp" / "qa" / "pages" / "BasePage.java"
    java_app_page = java_dir / "src" / "main" / "java" / "com" / "corp" / "qa" / "pages" / "AppPage.java"
    java_test = java_dir / "src" / "test" / "java" / "com" / "corp" / "qa" / "tests" / "AutomationSuiteTest.java"

    check(java_pom.exists() and java_testng.exists() and java_app_page.exists() and java_test.exists(), "Java Maven + TestNG suite structure exists")
    if java_test.exists():
        j_content = java_test.read_text(encoding="utf-8")
        check("waitForApiResponse" in j_content or "waitForResponse" in j_content, "Java suite implements API response interception")
        check("200" in j_content and "201" in j_content, "Java suite checks HTTP status codes [200, 201]")

    # 5. TypeScript Verification
    ts_dir = OUTPUT_DIR / "TypeScript_Playwright"
    ts_pkg = ts_dir / "package.json"
    ts_cfg = ts_dir / "playwright.config.ts"
    ts_app_page = ts_dir / "pages" / "AppPage.ts"
    ts_test = ts_dir / "tests" / "automation_suite.spec.ts"

    check(ts_pkg.exists() and ts_cfg.exists() and ts_app_page.exists() and ts_test.exists(), "TypeScript @playwright/test suite structure exists")
    if ts_test.exists():
        ts_content = ts_test.read_text(encoding="utf-8")
        check("waitForResponse" in ts_content, "TypeScript suite implements waitForResponse API check")
        check("200" in ts_content and "201" in ts_content, "TypeScript suite asserts status codes [200, 201]")

    # 6. JavaScript Verification
    js_dir = OUTPUT_DIR / "JavaScript_Playwright"
    js_pkg = js_dir / "package.json"
    js_cfg = js_dir / "playwright.config.js"
    js_app_page = js_dir / "pages" / "AppPage.js"
    js_test = js_dir / "tests" / "automation_suite.spec.js"

    check(js_pkg.exists() and js_cfg.exists() and js_app_page.exists() and js_test.exists(), "JavaScript @playwright/test suite structure exists")
    if js_test.exists():
        js_content = js_test.read_text(encoding="utf-8")
        check("waitForResponse" in js_content, "JavaScript suite implements waitForResponse API check")
        check("200" in js_content and "201" in js_content, "JavaScript suite asserts status codes [200, 201]")

    # 7. Progress Milestones
    pct_values = [p[1] for p in observed_progress]
    check(any(0.77 <= p <= 0.79 for p in pct_values), "Milestone 78% (Python synthesis) reported")
    check(any(0.81 <= p <= 0.83 for p in pct_values), "Milestone 82% (Java synthesis) reported")
    check(any(0.85 <= p <= 0.87 for p in pct_values), "Milestone 86% (TypeScript synthesis) reported")
    check(any(0.89 <= p <= 0.91 for p in pct_values), "Milestone 90% (JavaScript synthesis) reported")
    check(any(0.94 <= p <= 0.96 for p in pct_values), "Milestone 95% (ProjectScaffolder writing) reported")
    check(any(0.99 <= p <= 1.01 for p in pct_values), "Milestone 100% (Pipeline complete) reported")

    print("\n" + "=" * 80)
    print(f"PHASE 3 RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    if failed > 0:
        return 1

    print("PHASE 3 MULTI-LANGUAGE SYNTHESIZER & SCAFFOLDER VERIFICATION PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

