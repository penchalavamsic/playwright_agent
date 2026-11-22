"""Corporate Project Scaffolder.

Constructs production-grade directory structures, writes synthesized Page Object
Models, Test Suites, configuration files, and Readmes to disk.
100% offline and deterministic.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from scaffolder.flow_codegen import build_flow_test
from core.report_generator import EnterpriseReportGenerator, derive_app_display_name
from core.workspace_manager import WorkspaceManager
from scaffolder.template_registry import TemplateRegistry, to_pascal_case, to_snake_case


class ProjectScaffolder:
    """Manages creation of corporate multi-language Playwright test repositories."""

    def __init__(self, registry: TemplateRegistry = None) -> None:
        self.registry = registry or TemplateRegistry()

    def _render_file(self, template, context, raw_content=''):
        if template.endswith('_test_scenario_1'):
            return build_flow_test(context, template.split('_')[0])
        if template == 'python_conftest':
            return (Path(__file__).parent / 'runtime_pytest.py').read_text(encoding='utf-8')
        if template in ('java_base_test', 'java_report_listener'):
            filename = 'BaseTest.java' if template == 'java_base_test' else 'EnterpriseReportListener.java'
            return (Path(__file__).parent / 'java_runtime' / filename).read_text(encoding='utf-8')
        return self.registry.render(template, context) if template else raw_content

    def build_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare template rendering context from AgentState."""
        report = state.get("inspection_report", {})
        elements = [dict(element, code_name=f"{element.get('text_or_label') or 'element'}_{index}")
                    for index, element in enumerate(report.get("elements", []), 1)]
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

        sequence_number = int(state.get("sequence_number") or 1)
        seq_str = f"{sequence_number:03d}"

        raw_flow = (state.get("user_flow_text") or "").strip()
        # Derive a concise, filesystem-safe slug from user_flow_text
        flow_words = to_snake_case(raw_flow).split("_")
        # Filter out generic filler words if long
        concise_words = [w for w in flow_words if w and w not in ("create", "automation", "script", "for", "the", "and", "verify", "whether", "it", "with", "status", "code")]
        slug_source = "_".join((concise_words or flow_words)[:5]) or "user_flow"
        flow_slug = slug_source[:40].strip("_") or "user_flow"
        flow_pascal = to_pascal_case(flow_slug)

        raw_profile = state.get("active_access_profile", "") or ""
        if raw_profile.strip() in ("", "None (Public URL)", "NONE", "PUBLIC"):
            active_access_profile = "PUBLIC"
        else:
            active_access_profile = WorkspaceManager.normalize_role(raw_profile)

        app_display_name, domain_label = derive_app_display_name(
            state.get("target_url", ""),
            report.get("page_title", ""),
        )

        return {
            "target_url": state.get("target_url", ""),
            "page_title": report.get("page_title", ""),
            "app_display_name": app_display_name,
            "domain_label": domain_label,
            "target_languages": state.get("target_languages", ["Python", "Java", "TypeScript", "JavaScript"]),
            "elements": elements,
            "search_element": search_element,
            "dashboard_element": dashboard_element,
            "target_apis": apis,
            "target_api": target_api,
            "scenarios": scenarios,
            "sequence_number": sequence_number,
            "seq_str": seq_str,
            "flow_slug": flow_slug,
            "flow_pascal": flow_pascal,
            "active_access_profile": active_access_profile,
            "login_locators": {field: {lang: code.removeprefix('page.') for lang, code in locators.items()}
                               for field, locators in report.get("login_locators", {}).items()},
        }

    def scaffold_project(self, output_dir: str, state: Dict[str, Any]) -> List[str]:
        """Synthesize and write all selected language project suites to output_dir."""
        out_path = WorkspaceManager.resolve_run_output_dir(
            output_dir, state.get("target_url", "")
        )
        out_path.mkdir(parents=True, exist_ok=True)
        created_files: List[str] = []

        wm = WorkspaceManager(out_path)
        wm.state['browser_settings'] = state.get('browser_settings', {})
        for role, creds in (state.get("account_credentials") or {}).items():
            if isinstance(creds, dict):
                pw = creds.get("password", "")
                if not pw and creds.get("password_b64"):
                    pw = WorkspaceManager.decode_password(creds["password_b64"])
                wm.add_or_update_account(role, creds.get("username", ""), pw)

        context = self.build_context(state)
        target_langs = context.get("target_languages", [])
        seq_str = context["seq_str"]
        flow_slug = context["flow_slug"]
        flow_pascal = context["flow_pascal"]
        active_profile = context["active_access_profile"]
        existing_java = out_path / 'Java_Playwright/src/test/java/com/corp/qa/tests'
        context['java_test_classes'] = sorted({p.stem for p in existing_java.glob('Test[0-9]*.java')} | {f'Test{seq_str}{flow_pascal}'})

        # -------------------------------------------------------------------
        # 0. .env, .env.example, access-profiles.json, .gitignore
        # -------------------------------------------------------------------
        created_files.extend(
            wm.write_env_and_profiles(
                active_role=active_profile,
                target_url=state.get("target_url", ""),
            )
        )

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
                (py_root / "pages" / "login_page.py", "python_login_page", ""),
                (py_root / "pages" / "app_page.py", "python_app_page", ""),
                (py_root / "tests" / "__init__.py", "", ""),
                (py_root / "tests" / f"{seq_str}_{flow_slug}.py", "python_test_scenario_1", ""),
                (py_root / "conftest.py", "python_conftest", ""),
                (py_root / "pytest.ini", "python_pytest_ini", ""),
                (py_root / "requirements.txt", "python_requirements", ""),
            ]
            for file_path, tpl_name, raw_content in files:
                content = self._render_file(tpl_name, context, raw_content)
                file_path.write_text(content, encoding="utf-8")
                created_files.append(str(file_path))

        if "Python" in target_langs:
            import core.report_generator as renderer
            renderer_path = py_root / "report_renderer.py"
            renderer_path.write_text(Path(renderer.__file__).read_text(encoding='utf-8'), encoding='utf-8')
            created_files.append(str(renderer_path))

        # -------------------------------------------------------------------
        # 3. Java Playwright Suite (Maven + TestNG)
        # -------------------------------------------------------------------
        if "Java" in target_langs:
            java_root = out_path / "Java_Playwright"
            pages_dir = java_root / "src" / "main" / "java" / "com" / "corp" / "qa" / "pages"
            tests_dir = java_root / "src" / "test" / "java" / "com" / "corp" / "qa" / "tests"
            listeners_dir = java_root / "src" / "test" / "java" / "com" / "corp" / "qa" / "listeners"
            pages_dir.mkdir(parents=True, exist_ok=True)
            tests_dir.mkdir(parents=True, exist_ok=True)
            listeners_dir.mkdir(parents=True, exist_ok=True)

            files = [
                (java_root / "pom.xml", "java_pom_xml", ""),
                (java_root / "testng.xml", "java_testng_xml", ""),
                (listeners_dir / "EnterpriseReportListener.java", "java_report_listener", ""),
                (pages_dir / "BasePage.java", "java_base_page", ""),
                (pages_dir / "LoginPage.java", "java_login_page", ""),
                (pages_dir / "AppPage.java", "java_app_page", ""),
                (tests_dir / "BaseTest.java", "java_base_test", ""),
                (tests_dir / f"Test{seq_str}{flow_pascal}.java", "java_test_scenario_1", ""),
            ]
            for file_path, tpl_name, raw_content in files:
                content = self._render_file(tpl_name, context, raw_content)
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
                (ts_root / "enterprise-reporter.js", "js_enterprise_reporter", ""),
                (ts_root / "pages" / "LoginPage.ts", "ts_login_page", ""),
                (ts_root / "pages" / "AppPage.ts", "ts_app_page", ""),
                (ts_root / "tests" / f"{seq_str}_{flow_slug}.spec.ts", "ts_test_scenario_1", ""),
            ]
            for file_path, tpl_name, raw_content in files:
                content = self._render_file(tpl_name, context, raw_content)
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
                (js_root / "enterprise-reporter.js", "js_enterprise_reporter", ""),
                (js_root / "pages" / "LoginPage.js", "js_login_page", ""),
                (js_root / "pages" / "AppPage.js", "js_app_page", ""),
                (js_root / "tests" / f"{seq_str}_{flow_slug}.spec.js", "js_test_scenario_1", ""),
            ]
            for file_path, tpl_name, raw_content in files:
                content = self._render_file(tpl_name, context, raw_content)
                file_path.write_text(content, encoding="utf-8")
                created_files.append(str(file_path))

        # -------------------------------------------------------------------
        # 6. Enterprise Complete-Suite-Test-Report Generation (Phase 7)
        # -------------------------------------------------------------------
        for language in target_langs:
            folder = out_path / (language + '_Playwright')
            if language == 'Python':
                assets = [('runtime_auth.py', folder / 'auth_session.py')]
            elif language in ('TypeScript', 'JavaScript'):
                assets = [('runtime_session.js', folder / 'session-fixtures.js')]
            elif language == 'Java':
                assets = [('java_runtime/SessionGuard.java', folder / 'src/test/java/com/corp/qa/tests/SessionGuard.java')]
            else:
                assets = []
            for source, destination in assets:
                destination.write_text((Path(__file__).parent / source).read_text(encoding='utf-8'), encoding='utf-8')
                created_files.append(str(destination))

        report_gen = EnterpriseReportGenerator(out_path)
        created_files.extend(report_gen.generate_from_agent_state(state))

        wm.record_run(
            sequence_number=context["sequence_number"],
            test_id=f"TP-IEEE829-{seq_str}",
            title=f"{seq_str}_{flow_slug}",
            access_profile=active_profile,
            target_url=state.get("target_url", ""),
            target_languages=target_langs,
            files=created_files,
        )
        proj_file = wm.save_project_state()
        created_files.append(str(proj_file))

        return created_files

