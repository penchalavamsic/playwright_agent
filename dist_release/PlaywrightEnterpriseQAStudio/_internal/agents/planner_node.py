"""Deterministic IEEE 829 Corporate Test Plan and Scenario Generator Node.

Correlates DOM Element inventory + Network Telemetry (APIs) + Parsed Intents
into professional IEEE 829 Test Plans and structured Playwright test scenarios
strictly following PLAN_TEMPLATE.md standards.
Zero LLM calls - 100% offline and deterministic.
"""

from __future__ import annotations

import datetime
import inspect
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

from agents.state import AgentState, ParsedFlowStep, TestScenarioSpec, TestStepSpec


def _emit_progress(state: AgentState, node_name: str, percent: float, message: str) -> None:
    cb = state.get("progress_callback")
    if not cb:
        return
    try:
        res = cb(node_name, percent, message)
        if inspect.isawaitable(res):
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(res)
            except RuntimeError:
                asyncio.run(res)
    except Exception:
        pass


def _find_best_matching_element(target_keyword: str, elements: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Match target keyword against discovered interactive DOM elements."""
    if not target_keyword or not elements:
        return None
    kw = target_keyword.strip().lower()

    # 1. Exact match on text_or_label
    for el in elements:
        label = (el.get("text_or_label") or "").strip().lower()
        if label == kw:
            return el

    # 2. Substring or word match in text_or_label
    for el in elements:
        label = (el.get("text_or_label") or "").strip().lower()
        if kw in label or (len(label) > 2 and label in kw):
            return el

    # 3. Match against tag or role or attributes
    for el in elements:
        role = (el.get("role") or "").strip().lower()
        tag = (el.get("tag") or "").strip().lower()
        attrs = el.get("attributes") or {}
        haystack = f"{role} {tag} {attrs.get('data-testid', '')} {attrs.get('id', '')} {attrs.get('name', '')}".lower()
        if kw in haystack:
            return el

    # 4. Fallback: return first visible button or input if keyword is generic
    if kw in ["button", "submit", "click"]:
        for el in elements:
            if el.get("role") == "button" or el.get("tag") == "button":
                return el
    if kw in ["input", "search", "query", "text"]:
        for el in elements:
            if el.get("tag") in ["input", "textarea"]:
                return el

    return None


def _find_best_matching_api(
    target_keyword: str, apis: List[Dict[str, Any]], expected_statuses: List[int]
) -> Optional[Dict[str, Any]]:
    """Find captured API telemetry matching keyword or expected status codes."""
    if not apis:
        return None
    kw = target_keyword.strip().lower() if target_keyword else ""

    # Check URL path match
    if kw and kw != "api":
        for api in apis:
            url_path = urlparse(api.get("url", "")).path.lower()
            if kw in url_path:
                return api

    # Check triggered_by_action match
    if kw and kw != "api":
        for api in apis:
            action = (api.get("triggered_by_action") or "").lower()
            if kw in action:
                return api

    # Match by status code
    if expected_statuses:
        for api in apis:
            if api.get("status_code") in expected_statuses:
                return api

    # Fallback to first non-empty API
    return apis[0] if apis else None


def _generate_markdown_test_plan(
    target_url: str,
    page_title: str,
    user_flow_text: str,
    parsed_steps: List[ParsedFlowStep],
    elements: List[Dict[str, Any]],
    apis: List[Dict[str, Any]],
    scenarios: List[TestScenarioSpec],
) -> str:
    """Render a fully compliant IEEE 829 Standard Test Plan adhering strictly to PLAN_TEMPLATE.md."""
    clean_page = page_title.strip() if page_title else "Application"
    module_name = clean_page.split()[0] if clean_page else "Core"
    section_name = "Primary Navigation" if any(s.action_type in ("CLICK", "NAVIGATE") for s in parsed_steps) else "Main"
    
    # Identify key control and action from parsed steps
    control_name = "Action Control"
    action_name = "Execute Flow"
    for s in parsed_steps:
        if s.action_type == "CLICK":
            control_name = s.target_keyword.capitalize() or "Button"
            action_name = f"Click {control_name}"
            break
        elif s.action_type in ("SEARCH", "FILL"):
            control_name = s.target_keyword.capitalize() or "Search Input"
            action_name = f"Input '{s.input_value}' and Submit"
            break

    # Jira-style title format per Rule 11
    jira_title = f'To verify the functionality of "{module_name}" → "{section_name}" → "{control_name}" → "{action_name}"'
    test_id = f"TP-IEEE829-{int(datetime.datetime.now().timestamp())}"

    # Target API details for Network Verification section
    target_api = None
    for a in apis:
        if a.get("status_code") in (200, 201):
            target_api = a
            break
    if not target_api and apis:
        target_api = apis[0]

    api_url = target_api.get("url", "${LIMAS_BASE_URL}/api") if target_api else "${LIMAS_BASE_URL}/api"
    api_method = target_api.get("method", "GET") if target_api else "GET"
    api_status = target_api.get("status_code", 200) if target_api else 200
    expected_status_str = "200, 201" if api_status in (200, 201) else str(api_status)
    api_payload_presence = "Yes (JSON keys: " + ", ".join(target_api.get("response_keys", [])[:5]) + ")" if target_api and target_api.get("response_keys") else "No / Standard response payload"

    # Format Steps and Expected Results section
    steps_formatted = []
    step_idx = 1
    for sc in scenarios:
        for s in sc.steps:
            loc_disp = s.locators.get("python", "N/A")
            loc_str = f" using locator `{loc_disp}`" if loc_disp and loc_disp != "N/A" else ""
            input_str = f" with value '{s.input_data}'" if s.input_data else ""
            status_str = f" Expected status: {s.expected_status_codes}." if s.expected_status_codes else ""
            step_text = (
                f"{step_idx}. Action: {s.action} on {s.element_name}{input_str}{loc_str}.\n"
                f"   Expected Result: {s.description}. Successfully interact without DOM ambiguity.{status_str}"
            )
            steps_formatted.append(step_text)
            step_idx += 1
            if step_idx > 12:  # Keep clear and concise
                break
        if step_idx > 12:
            break
    steps_block = "\n\n".join(steps_formatted) if steps_formatted else (
        "1. Action: Navigate to ${LIMAS_BASE_URL}.\n"
        "   Expected Result: Application loads successfully with HTTP 200.\n\n"
        "2. Action: Verify presence of core controls.\n"
        "   Expected Result: Controls are visible and ready for interaction."
    )

    # Format Multi-Language Locators Table (Appendix for execution teams)
    loc_rows = []
    for el in elements[:25]:
        eid = el.get("element_id", "")
        tag_role = f"{el.get('tag', '')} ({el.get('role', '')})" if el.get("role") else el.get("tag", "")
        label = (el.get("text_or_label") or "").replace("|", "\\|")[:25]
        locs = el.get("recommended_locator") or {}
        py_loc = f"`{locs.get('python', '')}`"
        java_loc = f"`{locs.get('java', '')}`"
        ts_loc = f"`{locs.get('ts', '')}`"
        loc_rows.append(f"| {eid} | {tag_role} | {label} | {py_loc} | {java_loc} | {ts_loc} |")
    locators_table = "\n".join(loc_rows) if loc_rows else "| - | - | - | - | - | - |"

    # Format Network Verification Table
    api_rows = []
    for a in apis[:15]:
        method = a.get("method", "GET")
        url_path = urlparse(a.get("url", "")).path or a.get("url", "")
        status = a.get("status_code", 0)
        resp_keys = ", ".join(a.get("response_keys", [])[:5]) or "[]"
        action = a.get("triggered_by_action", "page_load")
        target_status = "200, 201" if status in (200, 201) else str(status)
        api_rows.append(f"| `{method}` | `{url_path}` | `{status}` | `{target_status}` | `{resp_keys}` | {action} |")
    apis_table = "\n".join(api_rows) if api_rows else "| - | - | - | - | - | - |"

    md = f"""---
test_id: "{test_id}"
title: "{jira_title}"
module: "{module_name}"
page: "{clean_page}"
section: "{section_name}"
control: "{control_name}"
action: "{action_name}"
access_profile: "ADMIN"
priority: "High"
classification: "Read-only"
test_type: "Automated End-to-End & API Contract"
automation_candidate: true
plan_status: "approved"
script_status: "generated"
environment_variables:
  - "LIMAS_BASE_URL"
  - "TEST_ACCESS_PROFILE"
test_data:
  target_url: "{target_url}"
  flow_prompt: "{user_flow_text}"
related_script: "tests/test_automation_suite.py"
---

# Purpose

Verify the end-to-end functionality and backend API status code contracts for {module_name} ({clean_page}) when executing the user flow: "{user_flow_text}".

# Preconditions

- `${{LIMAS_BASE_URL}}` is reachable (configured for target: `{target_url}`).
- Credentials for `${{TEST_ACCESS_PROFILE}}` are configured.
- The required role and test data are available.
- The starting page is accessible without security blockades.

# Test Data

Use environment variables, runtime fixtures, or configuration keys:
- `${{LIMAS_BASE_URL}}`: `{target_url}`
- Access Profile: `ADMIN`
- Target Locators: Prioritized Playwright locators (`data-testid` &rarr; `id` &rarr; `role+name`).

# Steps and Expected Results

{steps_block}

# Network Verification

- Request URL: `{api_url}`
- HTTP Method: `{api_method}`
- Expected Status: `[{expected_status_str}]`
- Payload Presence: {api_payload_presence}
- Visible UI Result: Core interactive elements update state and remain responsive.

### Captured Network API & Status Code Verification Matrix

| Method | Endpoint Path | Observed Status | Target Assertion Status | Response Payload Keys | Triggered By Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
{apis_table}

# Expected Final Result

One clear and independently verifiable result: The automation flow completes deterministically with 100% UI locator fidelity and all backend API calls return expected status codes ({expected_status_str}).

# Classification

- Read-only or Data-changing: Read-only (Non-destructive safe probes only)
- Category: Positive, API, Functional E2E

# Restrictions

- Do not include credentials, tokens, cookies, authorization codes, or sensitive payloads.
- Do not repeat data-changing submissions.
- Do not manually navigate to simulate a successful result.
- Do not use static environment-specific data.

# Generation Status

- Test script generation: Complete (Python, Java, TypeScript, JavaScript)
- CI/CD execution: Ready
- Healing: Ready

# Dynamic Plan Rules

1. Use only behavior verified through Playwright MCP.
2. Verify one atomic behavior per plan.
3. Do not hardcode application URLs.
4. Do not hardcode usernames or passwords.
5. Do not hardcode user names, emails, request IDs, license IDs, hardware IDs, dates, User Groups, Profiles, Roles, feature names, versions, or local paths.
6. Use environment variables, access-profiles.json, runtime fixtures, or test-data configuration.
7. Select exactly one access profile:
   - SUPER_USER
   - ADMIN
   - SUPER_USER_ADMIN_USER
8. Keep every plan shareable between environments and team members.
9. CI/CD owns test execution.
10. The Healer may propose test-only changes later but must not change expected LIMAS behavior.
11. Plans must use this Jira-style title format:

To verify the functionality of "<Module>" → "<Section>" → "<Control>" → "<Action>"

---

## Appendix: UI Component & Multi-Language Locator Inventory

Prioritized corporate locator hierarchy: `data-testid` &rarr; `id` &rarr; `role + name` &rarr; `placeholder` &rarr; `label` &rarr; `text` &rarr; `css`.

| Element ID | Tag / Role | Label / Text | Python Playwright | Java Playwright | TS / JS Playwright |
| :--- | :--- | :--- | :--- | :--- | :--- |
{locators_table}
"""
    return md.strip()


def test_planner_node(state: AgentState) -> Dict[str, Any]:
    """Correlate DOM elements, captured APIs, and parsed user intent into IEEE 829 Test Plan."""
    _emit_progress(
        state,
        "TestPlannerNode",
        0.65,
        "Correlating live DOM & API telemetry into IEEE 829 Corporate Test Plan...",
    )

    target_url = state.get("target_url", "")
    user_flow_text = state.get("user_flow_text", "")
    output_dir = state.get("output_dir", "")
    parsed_step_dicts = state.get("parsed_flow_steps", [])
    report_dict = state.get("inspection_report", {})

    parsed_steps = [ParsedFlowStep(**s) for s in parsed_step_dicts]
    elements: List[Dict[str, Any]] = report_dict.get("elements", [])
    apis: List[Dict[str, Any]] = report_dict.get("captured_apis", [])
    page_title = report_dict.get("page_title", "")

    # -------------------------------------------------------------------------
    # Scenario 1: Primary User Flow & API Status Verification
    # -------------------------------------------------------------------------
    s1_steps: List[TestStepSpec] = []
    step_num = 1

    # First step: Navigate
    s1_steps.append(
        TestStepSpec(
            step_number=step_num,
            action="NAVIGATE",
            description=f"Navigate to application URL: {target_url}",
            element_name="Browser Context",
            locators={"python": f"page.goto('{target_url}')", "java": f"page.navigate('{target_url}')", "ts": f"await page.goto('{target_url}')", "js": f"await page.goto('{target_url}')"},
            input_data=target_url,
            api_url_pattern=target_url,
            expected_status_codes=[200],
        )
    )
    step_num += 1

    for p in parsed_steps:
        if p.action_type == "NAVIGATE":
            continue

        matched_el = _find_best_matching_element(p.target_keyword, elements)
        matched_locators = matched_el.get("recommended_locator", {}) if matched_el else {}
        el_label = matched_el.get("text_or_label") or p.target_keyword if matched_el else p.target_keyword

        if p.action_type in ["SEARCH", "FILL"]:
            s1_steps.append(
                TestStepSpec(
                    step_number=step_num,
                    action=p.action_type,
                    description=f"{p.action_type.capitalize()} value '{p.input_value}' into control '{el_label}'",
                    element_name=el_label,
                    locators=matched_locators,
                    input_data=p.input_value,
                    api_url_pattern="",
                    expected_status_codes=[200],
                )
            )
            step_num += 1

        elif p.action_type == "CLICK":
            s1_steps.append(
                TestStepSpec(
                    step_number=step_num,
                    action="CLICK",
                    description=f"Click interactive component '{el_label}'",
                    element_name=el_label,
                    locators=matched_locators,
                    input_data="",
                    api_url_pattern="",
                    expected_status_codes=[],
                )
            )
            step_num += 1

        elif p.action_type == "VERIFY_API":
            matched_api = _find_best_matching_api(p.target_keyword, apis, p.expected_status_codes)
            api_url = matched_api.get("url", "/api") if matched_api else "/api"
            target_codes = p.expected_status_codes if p.expected_status_codes else [200, 201]
            s1_steps.append(
                TestStepSpec(
                    step_number=step_num,
                    action="VERIFY_API",
                    description=f"Verify backend API response status ({target_codes}) for endpoint '{urlparse(api_url).path}'",
                    element_name="Network Event Listener",
                    locators={},
                    input_data="",
                    api_url_pattern=api_url,
                    expected_status_codes=target_codes,
                )
            )
            step_num += 1

        elif p.action_type == "VERIFY_UI":
            s1_steps.append(
                TestStepSpec(
                    step_number=step_num,
                    action="VERIFY_UI",
                    description=f"Verify visibility and readiness of UI component '{el_label}'",
                    element_name=el_label,
                    locators=matched_locators,
                    input_data="",
                    api_url_pattern="",
                    expected_status_codes=[],
                )
            )
            step_num += 1

    scenario_1 = TestScenarioSpec(
        scenario_id="TC-01",
        title="Primary User Flow & API Status Verification",
        category="Positive E2E",
        steps=s1_steps,
    )

    # -------------------------------------------------------------------------
    # Scenario 2: Page Load & Core UI Component Sanity
    # -------------------------------------------------------------------------
    s2_steps: List[TestStepSpec] = [
        TestStepSpec(
            step_number=1,
            action="NAVIGATE",
            description=f"Open target URL: {target_url}",
            element_name="Page",
            locators={"python": f"page.goto('{target_url}')", "java": f"page.navigate('{target_url}')", "ts": f"await page.goto('{target_url}')", "js": f"await page.goto('{target_url}')"},
            input_data=target_url,
            api_url_pattern=target_url,
            expected_status_codes=[200],
        ),
        TestStepSpec(
            step_number=2,
            action="VERIFY_UI",
            description=f"Verify Page Title equals or contains '{page_title}'",
            element_name="Document Title",
            locators={"python": "expect(page).to_have_title(...)", "java": "assertThat(page).hasTitle(...)", "ts": "await expect(page).toHaveTitle(...)", "js": "await expect(page).toHaveTitle(...)"},
            input_data=page_title,
            api_url_pattern="",
            expected_status_codes=[],
        ),
    ]
    s2_num = 3
    for el in elements[:5]:
        locs = el.get("recommended_locator", {})
        label = el.get("text_or_label") or el.get("element_id")
        s2_steps.append(
            TestStepSpec(
                step_number=s2_num,
                action="VERIFY_UI",
                description=f"Verify visibility of core control '{label}' ({el.get('tag')})",
                element_name=label,
                locators=locs,
                input_data="",
                api_url_pattern="",
                expected_status_codes=[],
            )
        )
        s2_num += 1

    scenario_2 = TestScenarioSpec(
        scenario_id="TC-02",
        title="Page Load & Core UI Component Sanity",
        category="UI Element Check",
        steps=s2_steps,
    )

    # -------------------------------------------------------------------------
    # Scenario 3: API Health & Contract Matrix Verification
    # -------------------------------------------------------------------------
    s3_steps: List[TestStepSpec] = []
    s3_num = 1
    target_apis = [a for a in apis if a.get("status_code") in (200, 201)]
    if not target_apis:
        target_apis = apis[:5]
    for a in target_apis[:5]:
        path = urlparse(a.get("url", "")).path
        method = a.get("method", "GET")
        keys = a.get("response_keys", [])
        status = a.get("status_code", 200)
        s3_steps.append(
            TestStepSpec(
                step_number=s3_num,
                action="VERIFY_API",
                description=f"Validate contract for {method} {path} (Expected Status: [{status}], Keys: {keys})",
                element_name=f"{method} {path}",
                locators={},
                input_data="",
                api_url_pattern=a.get("url", ""),
                expected_status_codes=[status],
            )
        )
        s3_num += 1

    scenario_3 = TestScenarioSpec(
        scenario_id="TC-03",
        title="API Health & Contract Matrix Verification",
        category="API Verification",
        steps=s3_steps,
    )

    scenarios = [scenario_1, scenario_2, scenario_3]

    # Generate the Markdown Test Plan adhering strictly to PLAN_TEMPLATE.md
    md_content = _generate_markdown_test_plan(
        target_url=target_url,
        page_title=page_title,
        user_flow_text=user_flow_text,
        parsed_steps=parsed_steps,
        elements=elements,
        apis=apis,
        scenarios=scenarios,
    )

    # Save outputs if output_dir specified
    created_files: List[str] = list(state.get("generated_files", []))
    if output_dir:
        docs_dir = Path(output_dir) / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)

        plan_path = docs_dir / "Test_Plan_IEEE829.md"
        plan_path.write_text(md_content, encoding="utf-8")
        created_files.append(str(plan_path.resolve()))

        har_path = docs_dir / "network_har_summary.json"
        har_path.write_text(json.dumps(apis, indent=2), encoding="utf-8")
        created_files.append(str(har_path.resolve()))

    _emit_progress(
        state,
        "TestPlannerNode",
        0.75,
        "IEEE 829 Test Plan strictly adhering to PLAN_TEMPLATE.md generated successfully.",
    )

    return {
        "test_plan_markdown": md_content,
        "test_scenarios": [sc.model_dump() for sc in scenarios],
        "generated_files": created_files,
    }
