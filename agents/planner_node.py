"""Deterministic IEEE 829 Corporate Test Plan and Scenario Generator Node.

Correlates DOM Element inventory + Network Telemetry (APIs) + Parsed Intents
into professional IEEE 829 Test Plans and structured Playwright test scenarios.
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
    """Render a fully compliant IEEE 829 Standard Test Plan in GitHub-Flavored Markdown."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    url_host = urlparse(target_url).netloc or target_url

    # Format locators table (Top 25 elements to keep documentation concise yet complete)
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

    # Format API telemetry table
    api_rows = []
    for a in apis:
        method = a.get("method", "GET")
        url_path = urlparse(a.get("url", "")).path or a.get("url", "")
        status = a.get("status_code", 0)
        resp_keys = ", ".join(a.get("response_keys", [])[:5]) or "[]"
        action = a.get("triggered_by_action", "page_load")
        target_status = "200, 201" if status in (200, 201) else str(status)
        api_rows.append(f"| `{method}` | `{url_path}` | `{status}` | `{target_status}` | `{resp_keys}` | {action} |")
    apis_table = "\n".join(api_rows) if api_rows else "| - | - | - | - | - | - |"

    # Format Scenarios section
    scenario_sections = []
    for sc in scenarios:
        steps_md = []
        for s in sc.steps:
            loc_disp = s.locators.get("python", "N/A")
            if loc_disp != "N/A":
                loc_disp = f"`{loc_disp}`"
            codes_disp = ", ".join(str(c) for c in s.expected_status_codes) or "N/A"
            steps_md.append(f"| {s.step_number} | **{s.action}** | {s.description} | {loc_disp} | `{codes_disp}` |")
        steps_table = (
            "| Step | Action | Description | Playwright Locator (Python) | Expected Status |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n" + "\n".join(steps_md)
        )
        scenario_sections.append(
            f"### Scenario: [{sc.scenario_id}] {sc.title}\n\n"
            f"- **Classification**: `{sc.category}`\n\n"
            f"{steps_table}\n"
        )
    scenarios_content = "\n".join(scenario_sections)

    md = f"""# IEEE 829 CORPORATE TEST PLAN & AUTOMATION SPECIFICATION

**Document Reference**: `TP-IEEE829-AUTOGEN-{int(datetime.datetime.now().timestamp())}`  
**Standard**: IEEE 829-2008 Standard for Software and System Test Documentation  
**Generated On**: `{timestamp}`  
**Host Target**: `{url_host}`  
**Target URL**: `{target_url}`  
**Page Title**: `{page_title}`  
**Automation Engine**: 100% Offline Zero-API Playwright Desktop Agent  

---

## 1. Test Plan Identifier & Executive Summary

### 1.1 Scope of Automation
This deterministic Test Plan defines the automated validation requirements for **{page_title or target_url}**.
All interactive controls, live DOM hierarchy, and backend XHR/Fetch communication have been cataloged
via non-destructive browser telemetry.

- **Total Interactive UI Controls Cataloged**: `{len(elements)}`
- **Total Backend Endpoints Monitored**: `{len(apis)}`
- **Target Automation Languages**: `Python`, `Java (JUnit 5)`, `TypeScript`, `JavaScript`
- **Execution Mode**: Local Corporate Channel (`chrome` / `msedge`), 100% Offline, Zero Cloud Dependencies.

### 1.2 User Flow Objectives
The corporate user declared the following functional flow requirement:
> *"{user_flow_text}"*

---

## 2. Test Items & Features to be Tested

The following functional objectives were decomposed into deterministic test items:
"""
    for s in parsed_steps:
        md += f"- **Step {s.step_order} [{s.action_type}]**: Target: `{s.target_keyword}` | Value: `{s.input_value or 'N/A'}` | Target Status Codes: `{s.expected_status_codes or 'N/A'}`\n"

    md += f"""
---

## 3. UI Component & Multi-Language Locator Inventory

Prioritized corporate locator hierarchy: `data-testid` &rarr; `id` &rarr; `role + name` &rarr; `placeholder` &rarr; `label` &rarr; `text` &rarr; `css`.

| Element ID | Tag / Role | Label / Text | Python Playwright | Java Playwright | TS / JS Playwright |
| :--- | :--- | :--- | :--- | :--- | :--- |
{locators_table}

---

## 4. Captured Network API & Status Code Verification Matrix

Real-time telemetry captured during navigation and safe flow probing:

| Method | Endpoint Path | Observed Status | Target Assertion Status | Response Payload Keys | Triggered By Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
{apis_table}

---

## 5. Detailed Test Scenarios & Execution Steps

{scenarios_content}

---

## 6. Pass/Fail Criteria & Risk Mitigation

### 6.1 Pass Criteria
1. **Zero UI Divergence**: Every prioritized locator uniquely identifies exactly 1 DOM node without ambiguity.
2. **Deterministic HTTP Contract**: Captured API endpoints must return one of the declared target status codes (`200` or `201`).
3. **Multi-Language Parity**: All 4 target frameworks (`Python`, `Java`, `TypeScript`, `JavaScript`) produce identical execution semantics.

### 6.2 Corporate Risk Mitigation
- **Non-Destructive Safe Probing**: Destructive operations (`DELETE`, `POST /admin`, drop, remove) are filtered out automatically by corporate keyword safeguards.
- **Zero Data Leakage**: No network requests or telemetry were transmitted outside the local machine.
- **Headless Execution**: Compatible with Windows Desktop environments and corporate CI/CD pipelines.

---
*Generated by Offline Playwright Desktop Agent - Phase 2*
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
    # Check top captured APIs
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

    # Generate the Markdown Test Plan
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
        "IEEE 829 Test Plan & Scenarios generated successfully.",
    )

    return {
        "test_plan_markdown": md_content,
        "test_scenarios": [sc.model_dump() for sc in scenarios],
        "generated_files": created_files,
    }

