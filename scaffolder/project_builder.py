"""Corporate Project Scaffolder.

Constructs production-grade directory structures, writes synthesized Page Object
Models, Test Suites, configuration files, and Readmes to disk.
100% offline and deterministic.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from scaffolder.template_registry import TemplateRegistry


class ProjectScaffolder:
    """Manages creation of corporate multi-language Playwright test repositories."""

    def __init__(self, registry: TemplateRegistry = None) -> None:
        self.registry = registry or TemplateRegistry()

    def build_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare template rendering context from AgentState."""
        report = state.get("inspection_report", {})
        elements = report.get("elements", [])
        apis = report.get("captured_apis", [])
        scenarios = state.get("test_scenarios", [])

        # Find key interactive controls
        search_element = None
        dashboard_element = None

        for el in elements:
            label = (el.get("text_or_label") or "").lower()
            tag = el.get("tag", "").lower()
            role = (el.get("role") or "").lower()
            attrs = el.get("attributes", {})
            haystack = f"{label} {tag} {role} {attrs.get('id', '')} {attrs.get('placeholder', '')}".lower()

            if not search_element and ("search" in haystack or tag == "input"):
                search_element = el
            if not dashboard_element and ("dashboard" in haystack or role == "tab"):
                dashboard_element = el

        # Target API for TC-01 status interception
        target_api = None
        for a in apis:
            if a.get("status_code") in (200, 201) and ("/search" in a.get("url", "") or "/dashboard" in a.get("url", "") or "/api" in a.get("url", "")):
                target_api = {
                    "url": a.get("url", ""),
                    "url_pattern": a.get("url", "").split("?")[0].split("/")[-1] or "api",
                    "status_code": a.get("status_code", 200),
                    "expected_status_codes": [200, 201],
                }
                break
        if not target_api and apis:
            first_api = apis[0]
            target_api = {
                "url": first_api.get("url", ""),
                "url_pattern": first_api.get("url", "").split("?")[0].split("/")[-1] or "api",
                "status_code": first_api.get("status_code", 200),
                "expected_status_codes": [200, 201],
            }

        return {
            "target_url": state.get("target_url", ""),
            "page_title": report.get("page_title", ""),
            "target_languages": state.get("target_languages", ["Python", "Java", "TypeScript", "JavaScript"]),
            "elements": elements,
            "search_element": search_element,
            "dashboard_element": dashboard_element,
            "target_apis": apis,
            "target_api": target_api,
            "scenarios": scenarios,
        }

    def scaffold_project(self, output_dir: str, state: Dict[str, Any]) -> List[str]:
        """Synthesize and write all selected language project suites to output_dir."""
        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        context = self.build_context(state)
        target_langs = context.get("target_languages", [])

        # -------------------------------------------------------------------
        # 1. Master README.md & Docs copy
        # -------------------------------------------------------------------
        readme_content = self.registry.render("master_readme", context)
        readme_path = out_path / "README.md"
        readme_path.write_text(readme_content, encoding="utf-8")
        created_files.append(str(readme_path))

        docs_dir = out_path / "docs"
        docs_dir.mkdir(parents=True, exist_ok=True)
        test_plan_path = docs_dir / "Test_Plan_IEEE829.md"
        if not test_plan_path.exists() and state.get("test_plan_markdown"):
            test_plan_path.write_text(state["test_plan_markdown"], encoding="utf-8")
            created_files.append(str(test_plan_path))

        # -------------------------------------------------------------------
        # 2. Python Playwright Suite
        # -------------------------------------------------------------------
        if "Python" in target_langs:
            py_root = out_path / "Python_Playwright"
            (py_root / "pages").mkdir(parents=True, exist_ok=True)
            (py_root / "tests").mkdir(parents=True, exist_ok=True)

            files: List[Tuple[Path, str, str]] = [
                (py_root / "pages" / "__init__.py", "", ""),
                (py_root / "pages" / "base_page.py", "python_base_page", ""),
                (py_root / "pages" / "app_page.py", "python_app_page", ""),
                (py_root / "tests" / "__init__.py", "", ""),
                (py_root / "tests" / "test_automation_suite.py", "python_test_suite", ""),
                (py_root / "tests" / "001_primary_user_flow_and_api_verification.py", "python_test_scenario_1", ""),
                (py_root / "tests" / "002_page_load_and_core_ui_sanity.py", "python_test_scenario_2", ""),
                (py_root / "tests" / "003_api_health_and_contract_matrix.py", "python_test_scenario_3", ""),
                (py_root / "conftest.py", "python_conftest", ""),
                (py_root / "pytest.ini", "python_pytest_ini", ""),
                (py_root / "requirements.txt", "python_requirements", ""),
            ]
            for file_path, tpl_name, raw_content in files:
                content = self.registry.render(tpl_name, context) if tpl_name else raw_content
                file_path.write_text(content, encoding="utf-8")
                created_files.append(str(file_path))

        # -------------------------------------------------------------------
        # 3. Java Playwright Suite (Maven + TestNG)
        # -------------------------------------------------------------------
        if "Java" in target_langs:
            java_root = out_path / "Java_Playwright"
            pages_dir = java_root / "src" / "main" / "java" / "com" / "corp" / "qa" / "pages"
            tests_dir = java_root / "src" / "test" / "java" / "com" / "corp" / "qa" / "tests"
            pages_dir.mkdir(parents=True, exist_ok=True)
            tests_dir.mkdir(parents=True, exist_ok=True)

            files = [
                (java_root / "pom.xml", "java_pom_xml", ""),
                (java_root / "testng.xml", "java_testng_xml", ""),
                (pages_dir / "BasePage.java", "java_base_page", ""),
                (pages_dir / "AppPage.java", "java_app_page", ""),
                (tests_dir / "AutomationSuiteTest.java", "java_test_suite", ""),
                (tests_dir / "Test001PrimaryUserFlowAndApiVerification.java", "java_test_scenario_1", ""),
                (tests_dir / "Test002PageLoadAndCoreUiSanity.java", "java_test_scenario_2", ""),
                (tests_dir / "Test003ApiHealthAndContractMatrix.java", "java_test_scenario_3", ""),
            ]
            for file_path, tpl_name, raw_content in files:
                content = self.registry.render(tpl_name, context) if tpl_name else raw_content
                file_path.write_text(content, encoding="utf-8")
                created_files.append(str(file_path))

        # -------------------------------------------------------------------
        # 4. TypeScript Playwright Suite (@playwright/test)
        # -------------------------------------------------------------------
        if "TypeScript" in target_langs:
            ts_root = out_path / "TypeScript_Playwright"
            (ts_root / "pages").mkdir(parents=True, exist_ok=True)
            (ts_root / "tests").mkdir(parents=True, exist_ok=True)

            files = [
                (ts_root / "package.json", "ts_package_json", ""),
                (ts_root / "playwright.config.ts", "ts_playwright_config", ""),
                (ts_root / "pages" / "AppPage.ts", "ts_app_page", ""),
                (ts_root / "tests" / "automation_suite.spec.ts", "ts_test_suite", ""),
                (ts_root / "tests" / "001_primary_user_flow_and_api_verification.spec.ts", "ts_test_scenario_1", ""),
                (ts_root / "tests" / "002_page_load_and_core_ui_sanity.spec.ts", "ts_test_scenario_2", ""),
                (ts_root / "tests" / "003_api_health_and_contract_matrix.spec.ts", "ts_test_scenario_3", ""),
            ]
            for file_path, tpl_name, raw_content in files:
                content = self.registry.render(tpl_name, context) if tpl_name else raw_content
                file_path.write_text(content, encoding="utf-8")
                created_files.append(str(file_path))

        # -------------------------------------------------------------------
        # 5. JavaScript Playwright Suite (@playwright/test)
        # -------------------------------------------------------------------
        if "JavaScript" in target_langs:
            js_root = out_path / "JavaScript_Playwright"
            (js_root / "pages").mkdir(parents=True, exist_ok=True)
            (js_root / "tests").mkdir(parents=True, exist_ok=True)

            files = [
                (js_root / "package.json", "js_package_json", ""),
                (js_root / "playwright.config.js", "js_playwright_config", ""),
                (js_root / "pages" / "AppPage.js", "js_app_page", ""),
                (js_root / "tests" / "automation_suite.spec.js", "js_test_suite", ""),
                (js_root / "tests" / "001_primary_user_flow_and_api_verification.spec.js", "js_test_scenario_1", ""),
                (js_root / "tests" / "002_page_load_and_core_ui_sanity.spec.js", "js_test_scenario_2", ""),
                (js_root / "tests" / "003_api_health_and_contract_matrix.spec.js", "js_test_scenario_3", ""),
            ]
            for file_path, tpl_name, raw_content in files:
                content = self.registry.render(tpl_name, context) if tpl_name else raw_content
                file_path.write_text(content, encoding="utf-8")
                created_files.append(str(file_path))

        return created_files

