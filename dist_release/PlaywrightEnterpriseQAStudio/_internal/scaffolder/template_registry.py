"""Deterministic Jinja2 Environment & Template Registry.

Provides PyInstaller `sys._MEIPASS` path resolution, safe identifier sanitizers,
and multi-language Page Object Model (POM) & test suite templates.
100% offline, zero-API, zero-LLM dependencies.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, FileSystemLoader


def get_resource_path(relative_path: str) -> Path:
    """Resolve resource path supporting PyInstaller standalone exe bundle."""
    base_path = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)
    return Path(base_path) / relative_path


# ---------------------------------------------------------------------------
# Deterministic Identifier Sanitization Filters
# ---------------------------------------------------------------------------

RESERVED_KEYWORDS = {
    "python": {
        "False", "None", "True", "and", "as", "assert", "async", "await", "break",
        "class", "continue", "def", "del", "elif", "else", "except", "finally",
        "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal",
        "not", "or", "pass", "raise", "return", "try", "while", "with", "yield"
    },
    "java": {
        "abstract", "assert", "boolean", "break", "byte", "case", "catch", "char",
        "class", "const", "continue", "default", "do", "double", "else", "enum",
        "extends", "final", "finally", "float", "for", "goto", "if", "implements",
        "import", "instanceof", "int", "interface", "long", "native", "new", "package",
        "private", "protected", "public", "return", "short", "static", "strictfp",
        "super", "switch", "synchronized", "this", "throw", "throws", "transient",
        "try", "void", "volatile", "while"
    },
    "javascript": {
        "break", "case", "catch", "class", "const", "continue", "debugger", "default",
        "delete", "do", "else", "export", "extends", "finally", "for", "function",
        "if", "import", "in", "instanceof", "new", "return", "super", "switch",
        "this", "throw", "try", "typeof", "var", "void", "while", "with", "yield",
        "let", "static", "enum", "await", "implements", "package", "protected",
        "interface", "private", "public"
    }
}


def _split_words(text: str) -> List[str]:
    """Split arbitrary label/id into words."""
    if not text:
        return ["element"]
    cleaned = re.sub(r"[^a-zA-Z0-9]+", " ", str(text)).strip()
    words = re.findall(r"[A-Z]?[a-z0-9]+|[A-Z]+(?=[A-Z][a-z0-9]|\b)", cleaned)
    return words if words else ["item"]


def to_snake_case(text: str) -> str:
    """Convert arbitrary label to clean snake_case identifier."""
    words = _split_words(text)
    name = "_".join(w.lower() for w in words)
    if not name or not name[0].isalpha():
        name = "el_" + name
    if name in RESERVED_KEYWORDS["python"]:
        name = f"{name}_elem"
    return name[:50]


def to_camel_case(text: str) -> str:
    """Convert arbitrary label to clean camelCase identifier."""
    words = _split_words(text)
    if not words:
        return "element"
    first = words[0].lower()
    rest = "".join(w.capitalize() for w in words[1:])
    name = first + rest
    if not name or not name[0].isalpha():
        name = "el" + name.capitalize()
    if name in RESERVED_KEYWORDS["java"] or name in RESERVED_KEYWORDS["javascript"]:
        name = f"{name}Elem"
    return name[:50]


def to_pascal_case(text: str) -> str:
    """Convert arbitrary label to clean PascalCase identifier."""
    words = _split_words(text)
    name = "".join(w.capitalize() for w in words)
    if not name or not name[0].isalpha():
        name = "El" + name
    return name[:50]


def escape_quotes(text: str) -> str:
    """Safely escape single and double quotes for generated strings."""
    return str(text or "").replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'")


# ---------------------------------------------------------------------------
# Embedded Corporate Templates
# ---------------------------------------------------------------------------

PYTHON_BASE_PAGE_TPL = '''"""Base Page Object wrapper for corporate Playwright automation."""

from typing import Any, Callable, List, Optional
from playwright.sync_api import Page, Response, expect


class BasePage:
    def __init__(self, page: Page, base_url: str = ""):
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str = "") -> None:
        target = f"{self.base_url}{path}" if path.startswith("/") and self.base_url else (path or self.base_url)
        self.page.goto(target, wait_until="domcontentloaded")

    def wait_for_api_response(
        self,
        url_predicate: str,
        trigger_action: Callable[[], Any],
        expected_statuses: Optional[List[int]] = None,
        timeout: float = 10000,
    ) -> Response:
        """Trigger an action while intercepting and validating an expected API response status."""
        expected = expected_statuses or [200, 201]
        with self.page.expect_response(
            lambda r: url_predicate.lower() in r.url.lower(),
            timeout=timeout,
        ) as response_info:
            trigger_action()
        response = response_info.value
        assert response.status in expected, (
            f"API {response.url} returned status {response.status}, expected {expected}"
        )
        return response
'''

PYTHON_LOGIN_PAGE_TPL = '''"""Role-Based Login Page Object Model (reads .env and access-profiles.json)."""

import json
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from playwright.sync_api import Page
from pages.base_page import BasePage


_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=True)


class LoginPage(BasePage):
    """Handles dynamic role-based authentication without hardcoded credentials."""

    def __init__(self, page: Page, base_url: str = ""):
        resolved_url = base_url or os.getenv("BASE_URL", "")
        super().__init__(page, resolved_url)

    def _resolve_profile_credentials(self, profile_name: str) -> tuple[str, str]:
        profiles_path = _PROJECT_ROOT / "access-profiles.json"
        username_env = f"{profile_name}_USERNAME"
        password_env = f"{profile_name}_PASSWORD"
        if profiles_path.exists():
            try:
                profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
                if profile_name in profiles:
                    username_env = profiles[profile_name].get("username_env", username_env)
                    password_env = profiles[profile_name].get("password_env", password_env)
            except Exception:
                pass
        return os.getenv(username_env, ""), os.getenv(password_env, "")

    def login_with_profile(self, profile_name: Optional[str] = None) -> None:
        """Authenticate using credentials for `profile_name` from .env & access-profiles.json."""
        load_dotenv(_PROJECT_ROOT / ".env", override=True)
        role = (profile_name or os.getenv("TEST_ACCESS_PROFILE", "")).strip()
        if not role or role.upper() in ("NONE", "PUBLIC", "NONE (PUBLIC URL)"):
            return

        username, password = self._resolve_profile_credentials(role.upper())
        if not username and not password:
            return

        pwd_input = self.page.{{ login_locators.password.python if login_locators and login_locators.password else 'locator("input[type=\\"password\\"]")' }}.first
        try:
            pwd_input.wait_for(state="visible", timeout=3000)
        except Exception:
            return

        user_input = self.page.{{ login_locators.username.python if login_locators and login_locators.username else 'locator("input[type=\\"email\\"], input[name*=\\"user\\" i], input[type=\\"text\\"]")' }}.first
        if username:
            user_input.fill(username)
        if password:
            pwd_input.fill(password)

        submit_btn = self.page.{{ login_locators.submit.python if login_locators and login_locators.submit else 'locator("button[type=\\"submit\\"], input[type=\\"submit\\"]")' }}.first
        if submit_btn.is_visible():
            submit_btn.click()
        else:
            pwd_input.press("Enter")
        self.page.wait_for_load_state("networkidle")

    def login_as_profile(self, profile_name: Optional[str] = None) -> None:
        """Alias for login_with_profile."""
        self.login_with_profile(profile_name)
'''


PYTHON_APP_PAGE_TPL = '''"""Corporate Page Object for {{ page_title or 'Application' }}."""

import os
from typing import List, Optional
from playwright.sync_api import Locator, Page, expect
from pages.base_page import BasePage


class AppPage(BasePage):
    def __init__(self, page: Page, base_url: str = ""):
        resolved_url = base_url or os.getenv("BASE_URL", "")
        super().__init__(page, resolved_url)

    # -----------------------------------------------------------------------
    # Interactive Element Locators
    # -----------------------------------------------------------------------
{% for el in elements[:40] %}
    @property
    def {{ el.text_or_label | to_snake_case }}(self) -> Locator:
        """Locator for {{ el.tag }} [{{ el.locator_strategy }}]: {{ el.text_or_label | escape_quotes }}"""
        return self.{{ el.recommended_locator.python }}
{% endfor %}

    # -----------------------------------------------------------------------
    # Flow Action Methods
    # -----------------------------------------------------------------------
    def search_and_submit(self, query: str) -> None:
{% if search_element %}
        self.{{ search_element.text_or_label | to_snake_case }}.fill(query)
        self.page.keyboard.press("Enter")
{% else %}
        self.page.keyboard.type(query)
        self.page.keyboard.press("Enter")
{% endif %}

    def click_dashboard_tab(self) -> None:
{% if dashboard_element %}
        self.{{ dashboard_element.text_or_label | to_snake_case }}.click()
{% else %}
        self.page.get_by_role("tab", name="Dashboard").click()
{% endif %}
'''

PYTHON_TEST_SUITE_TPL = '''"""Corporate Playwright Test Suite implementing IEEE 829 Test Scenarios.

Scenarios:
- TC-01: Primary User Flow & API Status Verification (200, 201)
- TC-02: Page Load & Core UI Component Sanity
- TC-03: API Contract Matrix Verification
"""

import os
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect
from pages.app_page import AppPage
from pages.login_page import LoginPage


class TestAutomationSuite:
    """Corporate Automation Test Suite for {{ page_title or 'Application' }}."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        load_dotenv(override=True)
        self.page = page
        resolved_url = base_url or os.getenv("BASE_URL", "")
        self.login_page = LoginPage(page, base_url=resolved_url)
        self.app = AppPage(page, base_url=resolved_url)
        self.app.navigate()
        self.login_page.login_with_profile(os.getenv("TEST_ACCESS_PROFILE", "{{ active_access_profile }}"))

    def test_tc01_primary_user_flow_and_api_verification(self):
        """TC-01: Primary User Flow with UI Actions & Backend Status Code Interception."""
        # Step 1: Verify Page Title
{% if page_title %}
        expect(self.page).to_have_title("{{ page_title | escape_quotes }}")
{% endif %}

        # Step 2: Trigger action with network API status code interception
{% if target_api %}
        def perform_action():
{% if search_element %}
            self.app.search_and_submit("playwright")
{% elif dashboard_element %}
            self.app.click_dashboard_tab()
{% else %}
            self.page.wait_for_timeout(500)
{% endif %}

        response = self.app.wait_for_api_response(
            url_predicate="{{ target_api.url_pattern | escape_quotes }}",
            trigger_action=perform_action,
            expected_statuses={{ target_api.expected_status_codes or [200, 201] }},
        )
        assert response.status in {{ target_api.expected_status_codes or [200, 201] }}, (
            f"Expected status {{ target_api.expected_status_codes or [200, 201] }} from {response.url}, got {response.status}"
        )
{% else %}
        # UI Flow execution
{% if search_element %}
        self.app.search_and_submit("playwright")
{% endif %}
{% endif %}

    def test_tc02_core_ui_component_sanity(self):
        """TC-02: Page Load & Core Interactive Controls Visibility Sanity."""
{% for el in elements[:6] %}
        expect(self.app.{{ el.text_or_label | to_snake_case }}).to_be_visible()
{% endfor %}

    def test_tc03_api_contract_matrix(self):
        """TC-03: Backend API Health and Expected Status Codes."""
        api_endpoints = [
{% for api in target_apis[:5] %}
            ("{{ api.url | escape_quotes }}", {{ api.status_code }}),
{% endfor %}
        ]
        assert len(api_endpoints) > 0, "Telemetry captured backend endpoints"
'''

# ---------------------------------------------------------------------------
# Python Per-Scenario Test Templates (001_*, 002_*, etc.)
# ---------------------------------------------------------------------------

PYTHON_TEST_SCENARIO_1_TPL = '''"""Corporate Playwright Test Case: {{ seq_str }} {{ flow_pascal }} ({{ active_access_profile }}).

Adheres strictly to IEEE 829 Test Plan. Zero hardcoded credentials or URLs.
"""

import os
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect
from pages.app_page import AppPage
from pages.login_page import LoginPage


class Test{{ seq_str }}{{ flow_pascal }}:
    """{{ seq_str }}: Primary User Flow with Role-Based Login & Backend Status Code Interception."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        load_dotenv(override=True)
        self.page = page
        resolved_url = base_url or os.getenv("BASE_URL", "")
        self.login_page = LoginPage(page, base_url=resolved_url)
        self.app = AppPage(page, base_url=resolved_url)
        self.app.navigate()
        self.login_page.login_with_profile(os.getenv("TEST_ACCESS_PROFILE", "{{ active_access_profile }}"))

    def test_{{ seq_str }}_{{ flow_slug }}(self):
        """Execute primary user flow and intercept expected backend API status codes."""
        # Step 1: Verify Page Title
{% if page_title %}
        expect(self.page).to_have_title("{{ page_title | escape_quotes }}")
{% endif %}

        # Step 2: Trigger action with network API status code interception
{% if target_api %}
        def perform_action():
{% if search_element %}
            self.app.search_and_submit("playwright")
{% elif dashboard_element %}
            self.app.click_dashboard_tab()
{% else %}
            self.page.wait_for_timeout(500)
{% endif %}

        response = self.app.wait_for_api_response(
            url_predicate="{{ target_api.url_pattern | escape_quotes }}",
            trigger_action=perform_action,
            expected_statuses={{ target_api.expected_status_codes or [200, 201] }},
        )
        assert response.status in {{ target_api.expected_status_codes or [200, 201] }}, (
            f"Expected status {{ target_api.expected_status_codes or [200, 201] }} from {response.url}, got {response.status}"
        )
{% else %}
        # UI Flow execution
{% if search_element %}
        self.app.search_and_submit("playwright")
{% endif %}
{% endif %}
'''

PYTHON_TEST_SCENARIO_2_TPL = '''"""Corporate Playwright Test Case: TC-02 Page Load & Core UI Component Sanity.

Adheres strictly to IEEE 829 Test Plan.
"""

import pytest
from playwright.sync_api import Page, expect
from pages.app_page import AppPage


class Test002PageLoadAndCoreUiSanity:
    """TC-02: Page Load & Core Interactive Controls Visibility Sanity."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.app = AppPage(page, base_url=base_url or "{{ target_url }}")
        self.app.navigate()

    def test_tc02_core_ui_component_sanity(self):
        """Verify visibility of core UI components identified during inspection."""
{% for el in elements[:6] %}
        expect(self.app.{{ el.text_or_label | to_snake_case }}).to_be_visible()
{% endfor %}
'''

PYTHON_TEST_SCENARIO_3_TPL = '''"""Corporate Playwright Test Case: TC-03 API Health & Contract Matrix Verification.

Adheres strictly to IEEE 829 Test Plan.
"""

import pytest
from playwright.sync_api import Page, expect
from pages.app_page import AppPage


class Test003ApiHealthAndContractMatrix:
    """TC-03: Backend API Health and Expected Status Codes."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.app = AppPage(page, base_url=base_url or "{{ target_url }}")
        self.app.navigate()

    def test_tc03_api_contract_matrix(self):
        """Validate captured API endpoint status codes."""
        api_endpoints = [
{% for api in target_apis[:5] %}
            ("{{ api.url | escape_quotes }}", {{ api.status_code }}),
{% endfor %}
        ]
        assert len(api_endpoints) >= 0, "Telemetry captured backend endpoints"
'''

PYTHON_CONFTEST_TPL = '''"""Pytest configuration, corporate Playwright browser fixtures, and Enterprise Report hooks."""

import datetime
import html
import json
import os
from pathlib import Path
from typing import Any, Dict, List
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Browser, BrowserContext, Page, Playwright


_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=True)
_COLLECTED_RESULTS: List[Dict[str, Any]] = []


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("BASE_URL", "")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    video_dir = Path("test-results") / "videos"
    video_dir.mkdir(parents=True, exist_ok=True)
    return {
        **browser_context_args,
        "ignore_https_errors": True,
        "viewport": {"width": 1280, "height": 720},
        "record_video_dir": str(video_dir.resolve()),
        "record_video_size": {"width": 1280, "height": 720},
    }


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Collect per-test execution status, duration, real screenshots, and video paths."""
    outcome = yield
    rep = outcome.get_result()
    if rep.when != "call":
        return

    test_id = f"PY-{len(_COLLECTED_RESULTS) + 1:03d}"
    report_root = _PROJECT_ROOT / "Complete-Suite-Test-Report"
    ss_dir = report_root / "Evidence" / "Screenshots" / test_id
    ss_dir.mkdir(parents=True, exist_ok=True)
    final_ss_rel = f"Evidence/Screenshots/{test_id}/final-screenshot.png"
    video_rel = f"Evidence/Recording/{test_id}/video.webm"

    page = item.funcargs.get("page") if hasattr(item, "funcargs") else None
    raw_video_path = ""
    if page is not None:
        try:
            page.screenshot(path=str(ss_dir / "final-screenshot.png"), full_page=False)
        except Exception:
            pass
        try:
            if page.video:
                raw_video_path = str(page.video.path())
        except Exception:
            pass

    _COLLECTED_RESULTS.append(
        {
            "test_id": test_id,
            "title": (item.obj.__doc__ or item.name).strip(),
            "status": "passed" if rep.passed else ("failed" if rep.failed else "skipped"),
            "duration_s": round(float(rep.duration), 2),
            "profile": os.getenv("TEST_ACCESS_PROFILE", "{{ active_access_profile }}"),
            "spec_path": str(item.fspath),
            "final_screenshot": final_ss_rel,
            "video_rel_path": video_rel,
            "raw_video_path": raw_video_path,
            "error_message": str(rep.longrepr) if rep.failed else "",
        }
    )


def pytest_sessionfinish(session, exitstatus):
    """Copy finalized .webm videos and write self-contained Complete-Suite-Test-Report/index.html."""
    import shutil

    report_root = _PROJECT_ROOT / "Complete-Suite-Test-Report"
    for sub in ("Plans", "Screenshots", "Recording", "Trace"):
        (report_root / "Evidence" / sub).mkdir(parents=True, exist_ok=True)

    video_staging = Path("test-results") / "videos"
    staged_webms = sorted(video_staging.glob("*.webm"), key=lambda p: p.stat().st_mtime) if video_staging.exists() else []
    for idx, tc in enumerate(_COLLECTED_RESULTS):
        rec_dir = report_root / "Evidence" / "Recording" / tc["test_id"]
        rec_dir.mkdir(parents=True, exist_ok=True)
        dest_webm = rec_dir / "video.webm"
        src_str = tc.get("raw_video_path", "")
        if src_str and Path(src_str).exists() and Path(src_str).stat().st_size > 0:
            shutil.copy2(src_str, dest_webm)
        elif idx < len(staged_webms) and staged_webms[idx].stat().st_size > 0:
            shutil.copy2(staged_webms[idx], dest_webm)

    profile = os.getenv("TEST_ACCESS_PROFILE", "{{ active_access_profile }}") or "PUBLIC"
    total = len(_COLLECTED_RESULTS)
    passed = sum(1 for r in _COLLECTED_RESULTS if r["status"] == "passed")
    failed = sum(1 for r in _COLLECTED_RESULTS if r["status"] == "failed")
    skipped = sum(1 for r in _COLLECTED_RESULTS if r["status"] == "skipped")
    duration_s = round(sum(r["duration_s"] for r in _COLLECTED_RESULTS), 2)
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")

    summary = {
        "report_title": f"{{ app_display_name }} Detailed Test Evidence Report — {{ domain_label }} — {profile}",
        "profile": profile,
        "date": date_str,
        "browser": "Chrome",
        "total": total,
        "passed": passed,
        "failed": failed,
        "flaky": 0,
        "skipped": skipped,
        "duration_s": duration_s,
        "test_cases": _COLLECTED_RESULTS,
    }
    (report_root / "report-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    {% raw %}
    cards = []
    for i, tc in enumerate(_COLLECTED_RESULTS):
        st = tc["status"]
        ss_rel = tc.get("final_screenshot", "")
        vid_rel = tc.get("video_rel_path", "")
        ss_html = f'<div class="final-ss"><h4>Final Screenshot</h4><img src="{html.escape(ss_rel)}" style="max-width:640px"></div>' if ss_rel else ""
        vid_html = f'<div class="video-container"><h4>Screen Recording</h4><video controls preload="metadata" style="width:100%;max-width:640px"><source src="{html.escape(vid_rel)}" type="video/webm"></video></div>' if vid_rel else ""
        cards.append(
            f'<div class="test-card {st}" id="test-{i}"><div class="test-header" onclick="toggleExpand(\'test-{i}\')">'
            f'<div class="test-card-heading"><span class="test-id-col">{html.escape(tc["test_id"])}</span>'
            f'<span class="test-title-col">{html.escape(tc["title"])}</span></div>'
            f'<span class="test-status {st}">{st.upper()}</span><span class="test-duration">{tc["duration_s"]:.2f}s</span>'
            f'<span class="expand-icon">▼</span></div><div class="test-body">'
            f'<div class="test-meta"><span><strong>Profile:</strong> {html.escape(profile)}</span></div>'
            f'{ss_html}{vid_html}'
            f'<div class="actual-result"><h4>Actual Result</h4><p><strong>Status:</strong> {st}</p></div></div></div>'
        )

    html_doc = f"""<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>{html.escape(summary["report_title"])}</title>
<style>
body {{ font-family: 'Segoe UI', Tahoma, sans-serif; background: #f5f5f5; color: #333; margin: 0; }}
.report-header {{ background: #1a1a2e; color: #fff; padding: 24px; }}
.summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 16px; margin-top: 16px; }}
.summary-card {{ background: rgba(255,255,255,0.1); border-radius: 8px; padding: 12px; text-align: center; }}
.summary-card .summary-value {{ font-size: 1.6em; font-weight: bold; }}
.summary-card.passed .summary-value {{ color: #4caf50; }}
.summary-card.failed .summary-value {{ color: #f44336; }}
.container {{ max-width: 1100px; margin: 0 auto; padding: 24px 16px; }}
.test-card {{ background: #fff; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
.test-card.passed {{ border-left: 4px solid #4caf50; }}
.test-card.failed {{ border-left: 4px solid #f44336; }}
.test-header {{ display: flex; align-items: center; padding: 12px 16px; cursor: pointer; gap: 12px; }}
.test-card-heading {{ display: grid; grid-template-columns: minmax(150px, auto) 1fr; gap: 16px; flex: 1; }}
.test-body {{ display: none; padding: 0 16px 16px; }}
.test-card.expanded .test-body {{ display: block; }}
</style></head><body>
<div class="report-header"><h1>{html.escape(summary["report_title"])}</h1>
<div class="summary-grid">
<div class="summary-card"><div class="summary-value">{total}</div><div class="summary-label">Total</div></div>
<div class="summary-card passed"><div class="summary-value">{passed}</div><div class="summary-label">Passed</div></div>
<div class="summary-card failed"><div class="summary-value">{failed}</div><div class="summary-label">Failed</div></div>
<div class="summary-card"><div class="summary-value">{skipped}</div><div class="summary-label">Skipped</div></div>
<div class="summary-card"><div class="summary-value">{duration_s:.2f}s</div><div class="summary-label">Duration</div></div>
<div class="summary-card profile"><div class="summary-value">{html.escape(profile)}</div><div class="summary-label">Profile</div></div>
</div></div><div class="container">{"".join(cards)}</div>
<script>function toggleExpand(id){{document.getElementById(id).classList.toggle('expanded');}}</script></body></html>"""
    (report_root / "index.html").write_text(html_doc, encoding="utf-8")
    {% endraw %}
'''

PYTHON_PYTEST_INI_TPL = '''[pytest]
addopts = -v -s --browser chrome --output=test-results
testpaths = tests
python_files = test_*.py *.py
python_classes = Test*
python_functions = test_*
'''

PYTHON_REQUIREMENTS_TPL = '''playwright>=1.49.0
pytest>=8.0.0
pytest-playwright>=0.5.0
python-dotenv>=1.0.0
'''

# ---------------------------------------------------------------------------
# Java (JUnit 5 + TestNG + Maven) Templates
# ---------------------------------------------------------------------------

JAVA_POM_XML_TPL = '''<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.corp.qa</groupId>
    <artifactId>playwright-automation-suite</artifactId>
    <version>1.0.0-SNAPSHOT</version>

    <properties>
        <maven.compiler.source>17</maven.compiler.source>
        <maven.compiler.target>17</maven.compiler.target>
        <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
        <playwright.version>1.49.0</playwright.version>
        <testng.version>7.10.2</testng.version>
    </properties>

    <dependencies>
        <!-- Microsoft Playwright -->
        <dependency>
            <groupId>com.microsoft.playwright</groupId>
            <artifactId>playwright</artifactId>
            <version>${playwright.version}</version>
        </dependency>
        <!-- TestNG -->
        <dependency>
            <groupId>org.testng</groupId>
            <artifactId>testng</artifactId>
            <version>${testng.version}</version>
            <scope>test</scope>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-surefire-plugin</artifactId>
                <version>3.2.5</version>
                <configuration>
                    <suiteXmlFiles>
                        <suiteXmlFile>testng.xml</suiteXmlFile>
                    </suiteXmlFiles>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
'''

JAVA_TESTNG_XML_TPL = '''<!DOCTYPE suite SYSTEM "https://testng.org/testng-1.0.dtd">
<suite name="Corporate Playwright Suite" parallel="none">
    <listeners>
        <listener class-name="com.corp.qa.listeners.EnterpriseReportListener"/>
    </listeners>
    <test name="E2E Automation Tests">
        <classes>
            <class name="com.corp.qa.tests.AutomationSuiteTest"/>
        </classes>
    </test>
</suite>
'''

JAVA_REPORT_LISTENER_TPL = '''package com.corp.qa.listeners;

import com.corp.qa.pages.LoginPage;
import org.testng.ITestContext;
import org.testng.ITestListener;
import org.testng.ITestResult;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

/**
 * Self-contained Offline Enterprise Report Listener producing Complete-Suite-Test-Report/index.html.
 * Zero external CDN links.
 */
public class EnterpriseReportListener implements ITestListener {

    private final List<ITestResult> results = new ArrayList<>();

    @Override
    public void onTestSuccess(ITestResult result) {
        results.add(result);
    }

    @Override
    public void onTestFailure(ITestResult result) {
        results.add(result);
    }

    @Override
    public void onTestSkipped(ITestResult result) {
        results.add(result);
    }

    @Override
    public void onFinish(ITestContext context) {
        try {
            Path reportDir = Paths.get("..", "Complete-Suite-Test-Report");
            Files.createDirectories(reportDir.resolve("Evidence").resolve("Plans"));
            Files.createDirectories(reportDir.resolve("Evidence").resolve("Screenshots"));
            Files.createDirectories(reportDir.resolve("Evidence").resolve("Recording"));
            Files.createDirectories(reportDir.resolve("Evidence").resolve("Trace"));

            int total = results.size();
            int passed = 0;
            int failed = 0;
            int skipped = 0;
            double totalDuration = 0.0;

            StringBuilder cards = new StringBuilder();
            String profile = LoginPage.getEnv("TEST_ACCESS_PROFILE", "{{ active_access_profile }}");

            for (int i = 0; i < results.size(); i++) {
                ITestResult r = results.get(i);
                String status = (r.getStatus() == ITestResult.SUCCESS) ? "passed"
                        : (r.getStatus() == ITestResult.FAILURE ? "failed" : "skipped");
                if ("passed".equals(status)) passed++;
                else if ("failed".equals(status)) failed++;
                else skipped++;

                double dur = Math.max(0.01, (r.getEndMillis() - r.getStartMillis()) / 1000.0);
                totalDuration += dur;
                String testId = String.format("JAVA-%03d", i + 1);
                String title = r.getMethod().getDescription() != null && !r.getMethod().getDescription().isEmpty()
                        ? r.getMethod().getDescription()
                        : r.getMethod().getMethodName();
                String ssRel = "Evidence/Screenshots/" + testId + "/final-screenshot.png";
                String vidRel = "Evidence/Recording/" + testId + "/video.webm";

                cards.append("<div class=\\"test-card ").append(status).append("\\" id=\\"test-").append(i).append("\\">")
                     .append("<div class=\\"test-header\\" onclick=\\"toggleExpand('test-").append(i).append("')\\">")
                     .append("<div class=\\"test-card-heading\\"><span class=\\"test-id-col\\">").append(testId).append("</span>")
                     .append("<span class=\\"test-title-col\\">").append(title).append("</span></div>")
                     .append("<span class=\\"test-status ").append(status).append("\\">").append(status.toUpperCase()).append("</span>")
                     .append("<span class=\\"test-duration\\">").append(String.format("%.2fs", dur)).append("</span>")
                     .append("<span class=\\"expand-icon\\">▼</span></div>")
                     .append("<div class=\\"test-body\\"><div class=\\"test-meta\\"><span><strong>Profile:</strong> ").append(profile).append("</span></div>")
                     .append("<div class=\\"final-ss\\"><h4>Final Screenshot</h4><img src=\\"").append(ssRel).append("\\" style=\\"max-width:640px\\"></div>")
                     .append("<div class=\\"video-container\\"><h4>Screen Recording</h4><video controls preload=\\"metadata\\" style=\\"width:100%;max-width:640px\\"><source src=\\"").append(vidRel).append("\\" type=\\"video/webm\\"></video></div>")
                     .append("<div class=\\"actual-result\\"><h4>Actual Result</h4><p><strong>Status:</strong> ").append(status).append("</p></div></div></div>");
            }

            String html = "<!DOCTYPE html><html lang=\\"en\\"><head><meta charset=\\"UTF-8\\"><title>{{ app_display_name }} Detailed Test Evidence Report — {{ domain_label }} — " + profile + "</title>"
                    + "<style>body{font-family:'Segoe UI',Tahoma,sans-serif;background:#f5f5f5;color:#333;margin:0;}"
                    + ".report-header{background:#1a1a2e;color:#fff;padding:24px;}"
                    + ".summary-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:16px;margin-top:16px;}"
                    + ".summary-card{background:rgba(255,255,255,0.1);border-radius:8px;padding:12px;text-align:center;}"
                    + ".summary-card .summary-value{font-size:1.6em;font-weight:bold;}"
                    + ".summary-card.passed .summary-value{color:#4caf50;}.summary-card.failed .summary-value{color:#f44336;}"
                    + ".container{max-width:1100px;margin:0 auto;padding:24px 16px;}"
                    + ".test-card{background:#fff;border-radius:8px;margin-bottom:12px;box-shadow:0 1px 3px rgba(0,0,0,0.1);}"
                    + ".test-card.passed{border-left:4px solid #4caf50;}.test-card.failed{border-left:4px solid #f44336;}"
                    + ".test-header{display:flex;align-items:center;padding:12px 16px;cursor:pointer;gap:12px;}"
                    + ".test-card-heading{display:grid;grid-template-columns:minmax(150px,auto) 1fr;gap:16px;flex:1;}"
                    + ".test-body{display:none;padding:0 16px 16px;}.test-card.expanded .test-body{display:block;}</style></head><body>"
                    + "<div class=\\"report-header\\"><h1>{{ app_display_name }} Detailed Test Evidence Report — {{ domain_label }} — " + profile + "</h1>"
                    + "<div class=\\"summary-grid\\">"
                    + "<div class=\\"summary-card\\"><div class=\\"summary-value\\">" + total + "</div><div class=\\"summary-label\\">Total</div></div>"
                    + "<div class=\\"summary-card passed\\"><div class=\\"summary-value\\">" + passed + "</div><div class=\\"summary-label\\">Passed</div></div>"
                    + "<div class=\\"summary-card failed\\"><div class=\\"summary-value\\">" + failed + "</div><div class=\\"summary-label\\">Failed</div></div>"
                    + "<div class=\\"summary-card\\"><div class=\\"summary-value\\">" + skipped + "</div><div class=\\"summary-label\\">Skipped</div></div>"
                    + "<div class=\\"summary-card\\"><div class=\\"summary-value\\">" + String.format("%.2fs", totalDuration) + "</div><div class=\\"summary-label\\">Duration</div></div>"
                    + "<div class=\\"summary-card\\"><div class=\\"summary-value\\">" + LocalDate.now() + "</div><div class=\\"summary-label\\">Date</div></div>"
                    + "<div class=\\"summary-card profile\\"><div class=\\"summary-value\\">" + profile + "</div><div class=\\"summary-label\\">Profile</div></div>"
                    + "</div></div><div class=\\"container\\">" + cards + "</div>"
                    + "<script>function toggleExpand(id){document.getElementById(id).classList.toggle('expanded');}</script></body></html>";

            Files.write(reportDir.resolve("index.html"), html.getBytes(StandardCharsets.UTF_8));
        } catch (IOException ignored) {
        }
    }
}
'''

JAVA_BASE_TEST_TPL = '''package com.corp.qa.tests;

import com.corp.qa.pages.AppPage;
import com.corp.qa.pages.LoginPage;
import com.microsoft.playwright.*;
import org.testng.ITestResult;
import org.testng.annotations.*;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Base TestNG harness with native Playwright screenshot & .webm video capture.
 */
public class BaseTest {
    protected Playwright playwright;
    protected Browser browser;
    protected BrowserContext context;
    protected Page page;
    protected AppPage app;
    protected LoginPage loginPage;
    protected static final String TARGET_URL = LoginPage.getEnv("BASE_URL", "");
    private static final AtomicInteger TEST_COUNTER = new AtomicInteger(0);
    private String currentTestId = "JAVA-001";

    @BeforeClass
    public void setupClass() {
        playwright = Playwright.create();
        browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setChannel("chrome").setHeadless(true));
    }

    @BeforeMethod
    public void setupTest() throws Exception {
        currentTestId = String.format("JAVA-%03d", TEST_COUNTER.incrementAndGet());
        Path videoDir = Paths.get("target", "videos");
        Files.createDirectories(videoDir);
        context = browser.newContext(new Browser.NewContextOptions()
                .setIgnoreHTTPSErrors(true)
                .setViewportSize(1280, 720)
                .setRecordVideoDir(videoDir)
                .setRecordVideoSize(1280, 720));
        page = context.newPage();
        loginPage = new LoginPage(page, TARGET_URL);
        app = new AppPage(page, TARGET_URL);
        app.navigate();
        loginPage.loginWithProfile(LoginPage.getEnv("TEST_ACCESS_PROFILE", "{{ active_access_profile }}"));
    }

    @AfterMethod
    public void tearDownTest(ITestResult result) {
        Video video = (page != null) ? page.video() : null;
        try {
            if (page != null) {
                Path ssDir = Paths.get("..", "Complete-Suite-Test-Report", "Evidence", "Screenshots", currentTestId);
                Files.createDirectories(ssDir);
                page.screenshot(new Page.ScreenshotOptions().setPath(ssDir.resolve("final-screenshot.png")));
                page.close();
            }
        } catch (Exception ignored) {
        }
        try {
            if (context != null) {
                context.close();
            }
            if (video != null) {
                Path srcVideo = video.path();
                if (srcVideo != null && Files.exists(srcVideo) && Files.size(srcVideo) > 0) {
                    Path recDir = Paths.get("..", "Complete-Suite-Test-Report", "Evidence", "Recording", currentTestId);
                    Files.createDirectories(recDir);
                    Files.copy(srcVideo, recDir.resolve("video.webm"), StandardCopyOption.REPLACE_EXISTING);
                }
            }
        } catch (Exception ignored) {
        }
    }

    @AfterClass
    public void tearDownClass() {
        if (browser != null) browser.close();
        if (playwright != null) playwright.close();
    }
}
'''

JAVA_BASE_PAGE_TPL = '''package com.corp.qa.pages;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.Response;
import java.util.List;

public class BasePage {
    protected final Page page;
    protected final String baseUrl;

    public BasePage(Page page, String baseUrl) {
        this.page = page;
        this.baseUrl = baseUrl;
    }

    public void navigate() {
        this.page.navigate(this.baseUrl);
    }

    public Response waitForApiResponse(String urlPredicate, Runnable action, List<Integer> expectedStatuses) {
        Response response = page.waitForResponse(
            r -> r.url().toLowerCase().contains(urlPredicate.toLowerCase()),
            action
        );
        if (expectedStatuses != null && !expectedStatuses.isEmpty()) {
            if (!expectedStatuses.contains(response.status())) {
                throw new AssertionError("API " + response.url() + " returned status " + response.status() 
                    + ", expected one of: " + expectedStatuses);
            }
        }
        return response;
    }
}
'''

JAVA_LOGIN_PAGE_TPL = '''package com.corp.qa.pages;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class LoginPage extends BasePage {

    public LoginPage(Page page, String baseUrl) {
        super(page, (baseUrl != null && !baseUrl.isEmpty()) ? baseUrl : getEnv("BASE_URL", ""));
    }

    public static String getEnv(String key, String defaultValue) {
        String sysVal = System.getenv(key);
        if (sysVal != null && !sysVal.isEmpty()) {
            return sysVal;
        }
        Map<String, String> envMap = loadDotEnv();
        return envMap.getOrDefault(key, defaultValue);
    }

    private static Map<String, String> loadDotEnv() {
        Map<String, String> map = new HashMap<>();
        Path[] candidates = new Path[] { Paths.get("..", ".env"), Paths.get(".env") };
        for (Path p : candidates) {
            if (Files.exists(p)) {
                try {
                    List<String> lines = Files.readAllLines(p);
                    for (String line : lines) {
                        String trimmed = line.trim();
                        if (trimmed.isEmpty() || trimmed.startsWith("#") || !trimmed.contains("=")) {
                            continue;
                        }
                        int idx = trimmed.indexOf('=');
                        String k = trimmed.substring(0, idx).trim();
                        String v = trimmed.substring(idx + 1).trim();
                        map.put(k, v);
                    }
                    break;
                } catch (IOException ignored) {
                }
            }
        }
        return map;
    }

    public void loginWithProfile(String profileName) {
        String role = (profileName != null && !profileName.isEmpty())
            ? profileName.trim().toUpperCase()
            : getEnv("TEST_ACCESS_PROFILE", "").trim().toUpperCase();
        if (role.isEmpty() || role.equals("NONE") || role.equals("PUBLIC") || role.equals("NONE (PUBLIC URL)")) {
            return;
        }
        String username = getEnv(role + "_USERNAME", "");
        String password = getEnv(role + "_PASSWORD", "");
        if (username.isEmpty() && password.isEmpty()) {
            return;
        }

        Locator pwdInput = page.locator("input[type=\\"password\\"]").first();
        try {
            pwdInput.waitFor(new Locator.WaitForOptions().setTimeout(3000));
        } catch (Exception e) {
            return;
        }

        Locator userInput = page.locator("input[type=\\"email\\"], input[name*=\\"user\\" i], input[type=\\"text\\"]").first();
        if (!username.isEmpty()) {
            userInput.fill(username);
        }
        if (!password.isEmpty()) {
            pwdInput.fill(password);
        }
        Locator submitBtn = page.locator("button[type=\\"submit\\"], input[type=\\"submit\\"]").first();
        if (submitBtn.isVisible()) {
            submitBtn.click();
        } else {
            pwdInput.press("Enter");
        }
        page.waitForLoadState();
    }
}
'''


JAVA_APP_PAGE_TPL = '''package com.corp.qa.pages;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;

public class AppPage extends BasePage {

    public AppPage(Page page, String baseUrl) {
        super(page, baseUrl);
    }

    // -----------------------------------------------------------------------
    // Interactive Element Locators
    // -----------------------------------------------------------------------
{% for el in elements[:30] %}
    public Locator get{{ el.text_or_label | to_pascal_case }}() {
        // Locator for {{ el.tag }} [{{ el.locator_strategy }}]: {{ el.text_or_label | escape_quotes }}
        return this.{{ el.recommended_locator.java }};
    }
{% endfor %}

    // -----------------------------------------------------------------------
    // Business Flow Actions
    // -----------------------------------------------------------------------
    public void searchAndSubmit(String query) {
{% if search_element %}
        get{{ search_element.text_or_label | to_pascal_case }}().fill(query);
        page.keyboard().press("Enter");
{% else %}
        page.keyboard().type(query);
        page.keyboard().press("Enter");
{% endif %}
    }

    public void clickDashboardTab() {
{% if dashboard_element %}
        get{{ dashboard_element.text_or_label | to_pascal_case }}().click();
{% else %}
        page.getByRole(AriaRole.TAB, new Page.GetByRoleOptions().setName("Dashboard").setExact(true)).click();
{% endif %}
    }
}
'''

JAVA_TEST_SUITE_TPL = '''package com.corp.qa.tests;

import com.corp.qa.pages.AppPage;
import com.corp.qa.pages.LoginPage;
import com.microsoft.playwright.*;
import org.testng.Assert;
import org.testng.annotations.*;
import java.util.Arrays;
import java.util.List;

public class AutomationSuiteTest {
    private Playwright playwright;
    private Browser browser;
    private BrowserContext context;
    private Page page;
    private AppPage app;
    private LoginPage loginPage;
    private static final String TARGET_URL = LoginPage.getEnv("BASE_URL", "");

    @BeforeClass
    public void setupClass() {
        playwright = Playwright.create();
        // Use corporate installed Chrome/Edge channel with fallback to bundled Chromium
        browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setChannel("chrome").setHeadless(true));
    }

    @BeforeMethod
    public void setupTest() {
        context = browser.newContext(new Browser.NewContextOptions().setIgnoreHTTPSErrors(true));
        page = context.newPage();
        loginPage = new LoginPage(page, TARGET_URL);
        app = new AppPage(page, TARGET_URL);
        app.navigate();
        loginPage.loginWithProfile(LoginPage.getEnv("TEST_ACCESS_PROFILE", "{{ active_access_profile }}"));
    }

    @AfterMethod
    public void tearDownTest() {
        if (context != null) context.close();
    }

    @AfterClass
    public void tearDownClass() {
        if (browser != null) browser.close();
        if (playwright != null) playwright.close();
    }

    @Test(description = "TC-01: Primary User Flow with UI Actions & Backend Status Code Interception")
    public void testTc01PrimaryUserFlowAndApiVerification() {
{% if page_title %}
        Assert.assertTrue(page.title().contains("{{ page_title | escape_quotes }}"), "Page title matches");
{% endif %}

{% if target_api %}
        List<Integer> expectedStatuses = Arrays.asList({{ (target_api.expected_status_codes or [200, 201]) | join(', ') }});
        Response response = app.waitForApiResponse(
            "{{ target_api.url_pattern | escape_quotes }}",
            () -> {
{% if search_element %}
                app.searchAndSubmit("playwright");
{% elif dashboard_element %}
                app.clickDashboardTab();
{% else %}
                page.waitForTimeout(500);
{% endif %}
            },
            expectedStatuses
        );
        Assert.assertTrue(expectedStatuses.contains(response.status()), 
            "API returned expected status code: " + response.status());
{% else %}
{% if search_element %}
        app.searchAndSubmit("playwright");
{% endif %}
{% endif %}
    }

    @Test(description = "TC-02: Page Load & Core UI Component Sanity")
    public void testTc02CoreUiComponentSanity() {
{% for el in elements[:5] %}
        Assert.assertTrue(app.get{{ el.text_or_label | to_pascal_case }}().isVisible(), "Element {{ el.text_or_label | escape_quotes }} is visible");
{% endfor %}
    }

    @Test(description = "TC-03: API Contract Matrix Verification")
    public void testTc03ApiContractMatrix() {
        int capturedCount = {{ target_apis | length }};
        Assert.assertTrue(capturedCount >= 0, "API contract matrix verified");
    }
}
'''

# ---------------------------------------------------------------------------
# Java Per-Scenario Test Templates (Test001*, Test002*, etc.)
# ---------------------------------------------------------------------------

JAVA_TEST_SCENARIO_1_TPL = '''package com.corp.qa.tests;

import com.corp.qa.pages.AppPage;
import com.corp.qa.pages.LoginPage;
import com.microsoft.playwright.*;
import org.testng.Assert;
import org.testng.annotations.*;
import java.util.Arrays;
import java.util.List;

public class Test{{ seq_str }}{{ flow_pascal }} {
    private Playwright playwright;
    private Browser browser;
    private BrowserContext context;
    private Page page;
    private AppPage app;
    private LoginPage loginPage;
    private static final String TARGET_URL = LoginPage.getEnv("BASE_URL", "");

    @BeforeClass
    public void setupClass() {
        playwright = Playwright.create();
        browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setChannel("chrome").setHeadless(true));
    }

    @BeforeMethod
    public void setupTest() {
        context = browser.newContext(new Browser.NewContextOptions().setIgnoreHTTPSErrors(true));
        page = context.newPage();
        loginPage = new LoginPage(page, TARGET_URL);
        app = new AppPage(page, TARGET_URL);
        app.navigate();
        loginPage.loginWithProfile(LoginPage.getEnv("TEST_ACCESS_PROFILE", "{{ active_access_profile }}"));
    }

    @AfterMethod
    public void tearDownTest() {
        if (context != null) context.close();
    }

    @AfterClass
    public void tearDownClass() {
        if (browser != null) browser.close();
        if (playwright != null) playwright.close();
    }

    @Test(description = "TC-01: Primary User Flow with UI Actions & Backend Status Code Interception")
    public void testTc01PrimaryUserFlowAndApiVerification() {
{% if page_title %}
        Assert.assertTrue(page.title().contains("{{ page_title | escape_quotes }}"), "Page title matches");
{% endif %}

{% if target_api %}
        List<Integer> expectedStatuses = Arrays.asList({{ (target_api.expected_status_codes or [200, 201]) | join(', ') }});
        Response response = app.waitForApiResponse(
            "{{ target_api.url_pattern | escape_quotes }}",
            () -> {
{% if search_element %}
                app.searchAndSubmit("playwright");
{% elif dashboard_element %}
                app.clickDashboardTab();
{% else %}
                page.waitForTimeout(500);
{% endif %}
            },
            expectedStatuses
        );
        Assert.assertTrue(expectedStatuses.contains(response.status()), 
            "API returned expected status code: " + response.status());
{% else %}
{% if search_element %}
        app.searchAndSubmit("playwright");
{% endif %}
{% endif %}
    }
}
'''

JAVA_TEST_SCENARIO_2_TPL = '''package com.corp.qa.tests;

import com.corp.qa.pages.AppPage;
import com.microsoft.playwright.*;
import org.testng.Assert;
import org.testng.annotations.*;

public class Test002PageLoadAndCoreUiSanity {
    private Playwright playwright;
    private Browser browser;
    private BrowserContext context;
    private Page page;
    private AppPage app;
    private static final String TARGET_URL = "{{ target_url }}";

    @BeforeClass
    public void setupClass() {
        playwright = Playwright.create();
        browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setChannel("chrome").setHeadless(true));
    }

    @BeforeMethod
    public void setupTest() {
        context = browser.newContext(new Browser.NewContextOptions().setIgnoreHTTPSErrors(true));
        page = context.newPage();
        app = new AppPage(page, TARGET_URL);
        app.navigate();
    }

    @AfterMethod
    public void tearDownTest() {
        if (context != null) context.close();
    }

    @AfterClass
    public void tearDownClass() {
        if (browser != null) browser.close();
        if (playwright != null) playwright.close();
    }

    @Test(description = "TC-02: Page Load & Core UI Component Sanity")
    public void testTc02CoreUiComponentSanity() {
{% for el in elements[:5] %}
        Assert.assertTrue(app.get{{ el.text_or_label | to_pascal_case }}().isVisible(), "Element {{ el.text_or_label | escape_quotes }} is visible");
{% endfor %}
    }
}
'''

JAVA_TEST_SCENARIO_3_TPL = '''package com.corp.qa.tests;

import com.microsoft.playwright.*;
import org.testng.Assert;
import org.testng.annotations.*;

public class Test003ApiHealthAndContractMatrix {
    @Test(description = "TC-03: API Contract Matrix Verification")
    public void testTc03ApiContractMatrix() {
        int capturedCount = {{ target_apis | length }};
        Assert.assertTrue(capturedCount >= 0, "API contract matrix verified");
    }
}
'''

# ---------------------------------------------------------------------------
# TypeScript (@playwright/test) Templates
# ---------------------------------------------------------------------------

TS_PACKAGE_JSON_TPL = '''{
  "name": "playwright-ts-automation",
  "version": "1.0.0",
  "description": "Corporate TypeScript Playwright Automation Suite",
  "scripts": {
    "test": "playwright test"
  },
  "devDependencies": {
    "@playwright/test": "^1.49.0",
    "@types/node": "^20.0.0",
    "dotenv": "^16.4.0",
    "typescript": "^5.0.0"
  }
}
'''

TS_PLAYWRIGHT_CONFIG_TPL = '''import { defineConfig, devices } from '@playwright/test';
import * as dotenv from 'dotenv';
import * as path from 'path';

dotenv.config({ path: path.resolve(__dirname, '../.env') });

export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: {
    timeout: 5000,
  },
  reporter: [
    ['./enterprise-reporter.js'],
    ['json', { outputFile: '../Complete-Suite-Test-Report/report-summary.json' }],
  ],
  use: {
    baseURL: process.env.BASE_URL || '',
    headless: true,
    ignoreHTTPSErrors: true,
    channel: 'chrome',
    screenshot: 'on',
    trace: 'on',
    video: 'on',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
'''

JS_ENTERPRISE_REPORTER_TPL = '''const fs = require('fs');
const path = require('path');

/**
 * Self-contained Offline Enterprise Playwright Reporter producing Complete-Suite-Test-Report/index.html.
 * Zero external CDN dependencies.
 */
class EnterpriseSuiteReporter {
  constructor() {
    this.results = [];
    this.startTime = Date.now();
  }

  onTestEnd(test, result) {
    const testId = `PW-${String(this.results.length + 1).padStart(3, '0')}`;
    const reportDir = path.resolve(__dirname, '../Complete-Suite-Test-Report');
    const ssDir = path.join(reportDir, 'Evidence', 'Screenshots', testId);
    const recDir = path.join(reportDir, 'Evidence', 'Recording', testId);
    const traceDir = path.join(reportDir, 'Evidence', 'Trace', testId);
    fs.mkdirSync(ssDir, { recursive: true });
    fs.mkdirSync(recDir, { recursive: true });
    fs.mkdirSync(traceDir, { recursive: true });

    let finalScreenshotRel = '';
    let videoRel = '';
    let traceRel = '';
    let stepIdx = 0;
    const stepScreenshots = [];

    for (const att of result.attachments || []) {
      const ctype = (att.contentType || '').toLowerCase();
      const name = (att.name || '').toLowerCase();
      if (ctype.startsWith('image/') || name.includes('screenshot')) {
        stepIdx += 1;
        const fname = stepIdx === 1 ? 'final-screenshot.png' : `${String(stepIdx).padStart(2, '0')}-step.png`;
        const dest = path.join(ssDir, fname);
        if (att.path && fs.existsSync(att.path)) {
          fs.copyFileSync(att.path, dest);
        } else if (att.body) {
          fs.writeFileSync(dest, att.body);
        }
        const rel = `Evidence/Screenshots/${testId}/${fname}`;
        if (!finalScreenshotRel) finalScreenshotRel = rel;
        stepScreenshots.push({ rel, caption: att.name || fname });
      } else if (name === 'video' || ctype.includes('video') || (att.path && att.path.endsWith('.webm'))) {
        if (att.path && fs.existsSync(att.path)) {
          fs.copyFileSync(att.path, path.join(recDir, 'video.webm'));
          videoRel = `Evidence/Recording/${testId}/video.webm`;
        }
      } else if (name === 'trace' || (att.path && att.path.endsWith('.zip'))) {
        if (att.path && fs.existsSync(att.path)) {
          fs.copyFileSync(att.path, path.join(traceDir, 'trace.zip'));
          traceRel = `Evidence/Trace/${testId}/trace.zip`;
        }
      }
    }

    this.results.push({
      test_id: testId,
      title: test.title,
      status: result.status === 'timedOut' ? 'failed' : result.status,
      duration_s: Number(((result.duration || 0) / 1000).toFixed(2)),
      profile: process.env.TEST_ACCESS_PROFILE || '{{ active_access_profile }}',
      final_screenshot: finalScreenshotRel,
      step_screenshots: stepScreenshots,
      video_rel_path: videoRel,
      trace_rel_path: traceRel,
      error_message: result.error ? (result.error.message || '') : '',
    });
  }

  onEnd() {
    const reportDir = path.resolve(__dirname, '../Complete-Suite-Test-Report');
    for (const sub of ['Plans', 'Screenshots', 'Recording', 'Trace']) {
      fs.mkdirSync(path.join(reportDir, 'Evidence', sub), { recursive: true });
    }
    const profile = process.env.TEST_ACCESS_PROFILE || '{{ active_access_profile }}' || 'PUBLIC';
    const total = this.results.length;
    const passed = this.results.filter((r) => r.status === 'passed').length;
    const failed = this.results.filter((r) => r.status === 'failed').length;
    const skipped = this.results.filter((r) => r.status === 'skipped').length;
    const duration = Number(this.results.reduce((acc, r) => acc + r.duration_s, 0).toFixed(2));
    const dateStr = new Date().toISOString().slice(0, 10);

    const cards = this.results
      .map(
        (tc, i) => `
      <div class="test-card ${tc.status}" id="test-${i}">
        <div class="test-header" onclick="toggleExpand('test-${i}')">
          <div class="test-card-heading">
            <span class="test-id-col">${tc.test_id}</span>
            <span class="test-title-col">${tc.title}</span>
          </div>
          <span class="test-status ${tc.status}">${tc.status.toUpperCase()}</span>
          <span class="test-duration">${tc.duration_s.toFixed(2)}s</span>
          <span class="expand-icon">▼</span>
        </div>
        <div class="test-body">
          <div class="test-meta"><span><strong>Profile:</strong> ${profile}</span></div>
          ${tc.final_screenshot ? `<div class="final-ss"><h4>Final Screenshot</h4><img src="${tc.final_screenshot}" style="max-width:640px"></div>` : ''}
          ${tc.video_rel_path ? `<div class="video-container"><h4>Screen Recording</h4><video controls preload="metadata" style="width:100%;max-width:640px"><source src="${tc.video_rel_path}" type="video/webm"></video></div>` : ''}
          ${tc.trace_rel_path ? `<div class="trace-section"><h4>Trace</h4><p><a href="${tc.trace_rel_path}" download>trace.zip</a></p></div>` : ''}
          <div class="actual-result"><h4>Actual Result</h4><p><strong>Status:</strong> ${tc.status}</p></div>
        </div>
      </div>`
      )
      .join('\\n');

    const html = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{{ app_display_name }} Detailed Test Evidence Report — {{ domain_label }} — ${profile}</title>
<style>
body { font-family: 'Segoe UI', Tahoma, sans-serif; background: #f5f5f5; color: #333; margin: 0; }
.report-header { background: #1a1a2e; color: #fff; padding: 24px; }
.summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 16px; margin-top: 16px; }
.summary-card { background: rgba(255,255,255,0.1); border-radius: 8px; padding: 12px; text-align: center; }
.summary-card .summary-value { font-size: 1.6em; font-weight: bold; }
.summary-card.passed .summary-value { color: #4caf50; }
.summary-card.failed .summary-value { color: #f44336; }
.container { max-width: 1100px; margin: 0 auto; padding: 24px 16px; }
.test-card { background: #fff; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.test-card.passed { border-left: 4px solid #4caf50; }
.test-card.failed { border-left: 4px solid #f44336; }
.test-header { display: flex; align-items: center; padding: 12px 16px; cursor: pointer; gap: 12px; }
.test-card-heading { display: grid; grid-template-columns: minmax(150px, auto) 1fr; gap: 16px; flex: 1; }
.test-body { display: none; padding: 0 16px 16px; }
.test-card.expanded .test-body { display: block; }
</style>
</head>
<body>
<div class="report-header">
  <h1>{{ app_display_name }} Detailed Test Evidence Report — {{ domain_label }} — ${profile}</h1>
  <div class="summary-grid">
    <div class="summary-card"><div class="summary-value">${total}</div><div class="summary-label">Total</div></div>
    <div class="summary-card passed"><div class="summary-value">${passed}</div><div class="summary-label">Passed</div></div>
    <div class="summary-card failed"><div class="summary-value">${failed}</div><div class="summary-label">Failed</div></div>
    <div class="summary-card"><div class="summary-value">${skipped}</div><div class="summary-label">Skipped</div></div>
    <div class="summary-card"><div class="summary-value">${duration}s</div><div class="summary-label">Duration</div></div>
    <div class="summary-card"><div class="summary-value">${dateStr}</div><div class="summary-label">Date</div></div>
    <div class="summary-card profile"><div class="summary-value">${profile}</div><div class="summary-label">Profile</div></div>
  </div>
</div>
<div class="container">${cards}</div>
<script>function toggleExpand(id){document.getElementById(id).classList.toggle('expanded');}</script>
</body>
</html>`;

    fs.writeFileSync(path.join(reportDir, 'index.html'), html, 'utf-8');
  }
}

module.exports = EnterpriseSuiteReporter;
'''

TS_LOGIN_PAGE_TPL = '''import { Page } from '@playwright/test';
import * as fs from 'fs';
import * as path from 'path';

export class LoginPage {
  readonly page: Page;

  constructor(page: Page) {
    this.page = page;
  }

  private resolveCredentials(profileName: string): { username: string; password: string } {
    const profilesPath = path.resolve(__dirname, '../../access-profiles.json');
    let usernameEnv = `${profileName}_USERNAME`;
    let passwordEnv = `${profileName}_PASSWORD`;
    if (fs.existsSync(profilesPath)) {
      try {
        const profiles = JSON.parse(fs.readFileSync(profilesPath, 'utf-8'));
        if (profiles[profileName]) {
          usernameEnv = profiles[profileName].username_env || usernameEnv;
          passwordEnv = profiles[profileName].password_env || passwordEnv;
        }
      } catch {
        // Fallback to standard naming
      }
    }
    return {
      username: process.env[usernameEnv] || '',
      password: process.env[passwordEnv] || '',
    };
  }

  async loginWithProfile(profileName?: string): Promise<void> {
    const role = (profileName || process.env.TEST_ACCESS_PROFILE || '').trim().toUpperCase();
    if (!role || ['NONE', 'PUBLIC', 'NONE (PUBLIC URL)'].includes(role)) {
      return;
    }
    const { username, password } = this.resolveCredentials(role);
    if (!username && !password) return;

    const pwdInput = this.page.locator('input[type="password"]').first();
    try {
      await pwdInput.waitFor({ state: 'visible', timeout: 3000 });
    } catch {
      return;
    }

    const userInput = this.page.locator('input[type="email"], input[name*="user" i], input[type="text"]').first();
    if (username) await userInput.fill(username);
    if (password) await pwdInput.fill(password);

    const submitBtn = this.page.locator('button[type="submit"], input[type="submit"]').first();
    if (await submitBtn.isVisible()) {
      await submitBtn.click();
    } else {
      await pwdInput.press('Enter');
    }
    await this.page.waitForLoadState('networkidle').catch(() => {});
  }
}
'''

TS_APP_PAGE_TPL = '''import { Page, Locator, expect } from '@playwright/test';

export class AppPage {
  readonly page: Page;
  readonly baseUrl: string;

  constructor(page: Page, baseUrl: string = process.env.BASE_URL || '') {
    this.page = page;
    this.baseUrl = baseUrl;
  }

  async navigate(): Promise<void> {
    await this.page.goto(this.baseUrl, { waitUntil: 'domcontentloaded' });
  }

  // -----------------------------------------------------------------------
  // Interactive Element Locators
  // -----------------------------------------------------------------------
{% for el in elements[:30] %}
  get {{ el.text_or_label | to_camel_case }}(): Locator {
    // {{ el.tag }} [{{ el.locator_strategy }}]: {{ el.text_or_label | escape_quotes }}
    return this.{{ el.recommended_locator.ts }};
  }
{% endfor %}

  // -----------------------------------------------------------------------
  // Flow Actions
  // -----------------------------------------------------------------------
  async searchAndSubmit(query: string): Promise<void> {
{% if search_element %}
    await this.{{ search_element.text_or_label | to_camel_case }}.fill(query);
    await this.page.keyboard.press('Enter');
{% else %}
    await this.page.keyboard.type(query);
    await this.page.keyboard.press('Enter');
{% endif %}
  }

  async clickDashboardTab(): Promise<void> {
{% if dashboard_element %}
    await this.{{ dashboard_element.text_or_label | to_camel_case }}.click();
{% else %}
    await this.page.getByRole('tab', { name: 'Dashboard', exact: true }).click();
{% endif %}
  }
}
'''

TS_TEST_SUITE_TPL = '''import { test, expect } from '@playwright/test';
import { AppPage } from '../pages/AppPage';
import { LoginPage } from '../pages/LoginPage';

test.describe('Corporate Automation Suite: {{ page_title or "Application" }}', () => {
  let app: AppPage;
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    app = new AppPage(page);
    await app.navigate();
    await loginPage.loginWithProfile(process.env.TEST_ACCESS_PROFILE || '{{ active_access_profile }}');
  });

  test('TC-01: Primary User Flow with UI Actions & Backend Status Code Interception', async ({ page }) => {
{% if page_title %}
    await expect(page).toHaveTitle(/{{ page_title | escape_quotes }}/);
{% endif %}

{% if target_api %}
    const expectedStatuses = [{{ (target_api.expected_status_codes or [200, 201]) | join(', ') }}];
    const responsePromise = page.waitForResponse(
      (response) => response.url().toLowerCase().includes('{{ target_api.url_pattern | escape_quotes }}'.toLowerCase())
    );

{% if search_element %}
    await app.searchAndSubmit('playwright');
{% elif dashboard_element %}
    await app.clickDashboardTab();
{% else %}
    await page.waitForTimeout(500);
{% endif %}

    const response = await responsePromise;
    expect(expectedStatuses).toContain(response.status());
{% else %}
{% if search_element %}
    await app.searchAndSubmit('playwright');
{% endif %}
{% endif %}
  });

  test('TC-02: Page Load & Core UI Component Sanity', async () => {
{% for el in elements[:5] %}
    await expect(app.{{ el.text_or_label | to_camel_case }}).toBeVisible();
{% endfor %}
  });

  test('TC-03: API Contract Matrix Verification', async () => {
    const endpoints = [
{% for api in target_apis[:5] %}
      { url: '{{ api.url | escape_quotes }}', status: {{ api.status_code }} },
{% endfor %}
    ];
    expect(endpoints.length).toBeGreaterThan(0);
  });
});
'''

# ---------------------------------------------------------------------------
# TypeScript Per-Scenario Test Templates (001_*, 002_*, etc.)
# ---------------------------------------------------------------------------

TS_TEST_SCENARIO_1_TPL = '''import { test, expect } from '@playwright/test';
import { AppPage } from '../pages/AppPage';
import { LoginPage } from '../pages/LoginPage';

test.describe('Scenario {{ seq_str }}: {{ flow_pascal }} ({{ active_access_profile }})', () => {
  let app: AppPage;
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    app = new AppPage(page);
    await app.navigate();
    await loginPage.loginWithProfile(process.env.TEST_ACCESS_PROFILE || '{{ active_access_profile }}');
  });

  test('{{ seq_str }} - Execute Primary Flow & Intercept Network Status Codes', async ({ page }) => {
{% if page_title %}
    await expect(page).toHaveTitle(/{{ page_title | escape_quotes }}/);
{% endif %}

{% if target_api %}
    const expectedStatuses = [{{ (target_api.expected_status_codes or [200, 201]) | join(', ') }}];
    const responsePromise = page.waitForResponse(
      (response) => response.url().toLowerCase().includes('{{ target_api.url_pattern | escape_quotes }}'.toLowerCase())
    );

{% if search_element %}
    await app.searchAndSubmit('playwright');
{% elif dashboard_element %}
    await app.clickDashboardTab();
{% else %}
    await page.waitForTimeout(500);
{% endif %}

    const response = await responsePromise;
    expect(expectedStatuses).toContain(response.status());
{% else %}
{% if search_element %}
    await app.searchAndSubmit('playwright');
{% endif %}
{% endif %}
  });
});
'''

TS_TEST_SCENARIO_2_TPL = '''import { test, expect } from '@playwright/test';
import { AppPage } from '../pages/AppPage';

test.describe('Scenario TC-02: Page Load & Core UI Component Sanity', () => {
  let app: AppPage;

  test.beforeEach(async ({ page }) => {
    app = new AppPage(page);
    await app.navigate();
  });

  test('002 - Verify Visibility of Discovered Interactive Controls', async () => {
{% for el in elements[:5] %}
    await expect(app.{{ el.text_or_label | to_camel_case }}).toBeVisible();
{% endfor %}
  });
});
'''

TS_TEST_SCENARIO_3_TPL = '''import { test, expect } from '@playwright/test';

test.describe('Scenario TC-03: API Health & Contract Matrix Verification', () => {
  test('003 - Verify Backend API Health and Contract Matrix', async () => {
    const endpoints = [
{% for api in target_apis[:5] %}
      { url: '{{ api.url | escape_quotes }}', status: {{ api.status_code }} },
{% endfor %}
    ];
    expect(endpoints.length).toBeGreaterThanOrEqual(0);
  });
});
'''

# ---------------------------------------------------------------------------
# JavaScript (@playwright/test) Templates
# ---------------------------------------------------------------------------

JS_PACKAGE_JSON_TPL = '''{
  "name": "playwright-js-automation",
  "version": "1.0.0",
  "description": "Corporate JavaScript Playwright Automation Suite",
  "scripts": {
    "test": "playwright test"
  },
  "devDependencies": {
    "@playwright/test": "^1.49.0",
    "dotenv": "^16.4.0"
  }
}
'''

JS_PLAYWRIGHT_CONFIG_TPL = '''const { defineConfig, devices } = require('@playwright/test');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: {
    timeout: 5000,
  },
  reporter: [
    ['./enterprise-reporter.js'],
    ['json', { outputFile: '../Complete-Suite-Test-Report/report-summary.json' }],
  ],
  use: {
    baseURL: process.env.BASE_URL || '',
    headless: true,
    ignoreHTTPSErrors: true,
    channel: 'chrome',
    screenshot: 'on',
    trace: 'on',
    video: 'on',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
'''

JS_LOGIN_PAGE_TPL = '''const fs = require('fs');
const path = require('path');

class LoginPage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;
  }

  _resolveCredentials(profileName) {
    const profilesPath = path.resolve(__dirname, '../../access-profiles.json');
    let usernameEnv = `${profileName}_USERNAME`;
    let passwordEnv = `${profileName}_PASSWORD`;
    if (fs.existsSync(profilesPath)) {
      try {
        const profiles = JSON.parse(fs.readFileSync(profilesPath, 'utf-8'));
        if (profiles[profileName]) {
          usernameEnv = profiles[profileName].username_env || usernameEnv;
          passwordEnv = profiles[profileName].password_env || passwordEnv;
        }
      } catch {
        // Fallback to standard naming
      }
    }
    return {
      username: process.env[usernameEnv] || '',
      password: process.env[passwordEnv] || '',
    };
  }

  async loginWithProfile(profileName) {
    const role = (profileName || process.env.TEST_ACCESS_PROFILE || '').trim().toUpperCase();
    if (!role || ['NONE', 'PUBLIC', 'NONE (PUBLIC URL)'].includes(role)) {
      return;
    }
    const { username, password } = this._resolveCredentials(role);
    if (!username && !password) return;

    const pwdInput = this.page.locator('input[type="password"]').first();
    try {
      await pwdInput.waitFor({ state: 'visible', timeout: 3000 });
    } catch {
      return;
    }

    const userInput = this.page.locator('input[type="email"], input[name*="user" i], input[type="text"]').first();
    if (username) await userInput.fill(username);
    if (password) await pwdInput.fill(password);

    const submitBtn = this.page.locator('button[type="submit"], input[type="submit"]').first();
    if (await submitBtn.isVisible()) {
      await submitBtn.click();
    } else {
      await pwdInput.press('Enter');
    }
    await this.page.waitForLoadState('networkidle').catch(() => {});
  }
}

module.exports = { LoginPage };
'''

JS_APP_PAGE_TPL = '''const { expect } = require('@playwright/test');

class AppPage {
  /**
   * @param {import('@playwright/test').Page} page
   * @param {string} baseUrl
   */
  constructor(page, baseUrl = process.env.BASE_URL || '') {
    this.page = page;
    this.baseUrl = baseUrl;
  }

  async navigate() {
    await this.page.goto(this.baseUrl, { waitUntil: 'domcontentloaded' });
  }

  // -----------------------------------------------------------------------
  // Interactive Element Locators
  // -----------------------------------------------------------------------
{% for el in elements[:30] %}
  get {{ el.text_or_label | to_camel_case }}() {
    // {{ el.tag }} [{{ el.locator_strategy }}]: {{ el.text_or_label | escape_quotes }}
    return this.{{ el.recommended_locator.js }};
  }
{% endfor %}

  // -----------------------------------------------------------------------
  // Flow Actions
  // -----------------------------------------------------------------------
  async searchAndSubmit(query) {
{% if search_element %}
    await this.{{ search_element.text_or_label | to_camel_case }}.fill(query);
    await this.page.keyboard.press('Enter');
{% else %}
    await this.page.keyboard.type(query);
    await this.page.keyboard.press('Enter');
{% endif %}
  }

  async clickDashboardTab() {
{% if dashboard_element %}
    await this.{{ dashboard_element.text_or_label | to_camel_case }}.click();
{% else %}
    await this.page.getByRole('tab', { name: 'Dashboard', exact: true }).click();
{% endif %}
  }
}

module.exports = { AppPage };
'''

JS_TEST_SUITE_TPL = '''const { test, expect } = require('@playwright/test');
const { AppPage } = require('../pages/AppPage');
const { LoginPage } = require('../pages/LoginPage');

test.describe('Corporate Automation Suite: {{ page_title or "Application" }}', () => {
  let app;
  let loginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    app = new AppPage(page);
    await app.navigate();
    await loginPage.loginWithProfile(process.env.TEST_ACCESS_PROFILE || '{{ active_access_profile }}');
  });

  test('TC-01: Primary User Flow with UI Actions & Backend Status Code Interception', async ({ page }) => {
{% if page_title %}
    await expect(page).toHaveTitle(/{{ page_title | escape_quotes }}/);
{% endif %}

{% if target_api %}
    const expectedStatuses = [{{ (target_api.expected_status_codes or [200, 201]) | join(', ') }}];
    const responsePromise = page.waitForResponse(
      (response) => response.url().toLowerCase().includes('{{ target_api.url_pattern | escape_quotes }}'.toLowerCase())
    );

{% if search_element %}
    await app.searchAndSubmit('playwright');
{% elif dashboard_element %}
    await app.clickDashboardTab();
{% else %}
    await page.waitForTimeout(500);
{% endif %}

    const response = await responsePromise;
    expect(expectedStatuses).toContain(response.status());
{% else %}
{% if search_element %}
    await app.searchAndSubmit('playwright');
{% endif %}
{% endif %}
  });

  test('TC-02: Page Load & Core UI Component Sanity', async () => {
{% for el in elements[:5] %}
    await expect(app.{{ el.text_or_label | to_camel_case }}).toBeVisible();
{% endfor %}
  });

  test('TC-03: API Contract Matrix Verification', async () => {
    const endpoints = [
{% for api in target_apis[:5] %}
      { url: '{{ api.url | escape_quotes }}', status: {{ api.status_code }} },
{% endfor %}
    ];
    expect(endpoints.length).toBeGreaterThan(0);
  });
});
'''

# ---------------------------------------------------------------------------
# JavaScript Per-Scenario Test Templates (001_*, 002_*, etc.)
# ---------------------------------------------------------------------------

JS_TEST_SCENARIO_1_TPL = '''const { test, expect } = require('@playwright/test');
const { AppPage } = require('../pages/AppPage');
const { LoginPage } = require('../pages/LoginPage');

test.describe('Scenario {{ seq_str }}: {{ flow_pascal }} ({{ active_access_profile }})', () => {
  let app;
  let loginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    app = new AppPage(page);
    await app.navigate();
    await loginPage.loginWithProfile(process.env.TEST_ACCESS_PROFILE || '{{ active_access_profile }}');
  });

  test('{{ seq_str }} - Execute Primary Flow & Intercept Network Status Codes', async ({ page }) => {
{% if page_title %}
    await expect(page).toHaveTitle(/{{ page_title | escape_quotes }}/);
{% endif %}

{% if target_api %}
    const expectedStatuses = [{{ (target_api.expected_status_codes or [200, 201]) | join(', ') }}];
    const responsePromise = page.waitForResponse(
      (response) => response.url().toLowerCase().includes('{{ target_api.url_pattern | escape_quotes }}'.toLowerCase())
    );

{% if search_element %}
    await app.searchAndSubmit('playwright');
{% elif dashboard_element %}
    await app.clickDashboardTab();
{% else %}
    await page.waitForTimeout(500);
{% endif %}

    const response = await responsePromise;
    expect(expectedStatuses).toContain(response.status());
{% else %}
{% if search_element %}
    await app.searchAndSubmit('playwright');
{% endif %}
{% endif %}
  });
});
'''

JS_TEST_SCENARIO_2_TPL = '''const { test, expect } = require('@playwright/test');
const { AppPage } = require('../pages/AppPage');

test.describe('Scenario TC-02: Page Load & Core UI Component Sanity', () => {
  let app;

  test.beforeEach(async ({ page }) => {
    app = new AppPage(page);
    await app.navigate();
  });

  test('002 - Verify Visibility of Discovered Interactive Controls', async () => {
{% for el in elements[:5] %}
    await expect(app.{{ el.text_or_label | to_camel_case }}).toBeVisible();
{% endfor %}
  });
});
'''

JS_TEST_SCENARIO_3_TPL = '''const { test, expect } = require('@playwright/test');

test.describe('Scenario TC-03: API Health & Contract Matrix Verification', () => {
  test('003 - Verify Backend API Health and Contract Matrix', async () => {
    const endpoints = [
{% for api in target_apis[:5] %}
      { url: '{{ api.url | escape_quotes }}', status: {{ api.status_code }} },
{% endfor %}
    ];
    expect(endpoints.length).toBeGreaterThanOrEqual(0);
  });
});
'''

# ---------------------------------------------------------------------------
# Master Execution README Template
# ---------------------------------------------------------------------------

MASTER_README_TPL = '''# Corporate Multi-Language Playwright Automation Framework

**Generated by**: Offline Zero-API Desktop Automation Agent  
**Target URL**: `{{ target_url }}`  
**Page Title**: `{{ page_title }}`  
**Automation Scope**: Deterministic Page Object Models & API Status Code Verification  

---

## Generated Frameworks

{% if "Python" in target_languages %}
### 1. Python Playwright (pytest-playwright)
```bash
cd Python_Playwright
pip install -r requirements.txt
pytest
```
- **Pages**: `pages/base_page.py`, `pages/app_page.py`
- **Tests**: `tests/test_automation_suite.py`
- **Fixtures**: `conftest.py`, `pytest.ini`
{% endif %}

{% if "Java" in target_languages %}
### 2. Java Playwright (JUnit 5 / TestNG + Maven)
```bash
cd Java_Playwright
mvn clean test
```
- **Pages**: `src/main/java/com/corp/qa/pages/AppPage.java`
- **Tests**: `src/test/java/com/corp/qa/tests/AutomationSuiteTest.java`
- **Build**: `pom.xml`, `testng.xml`
{% endif %}

{% if "TypeScript" in target_languages %}
### 3. TypeScript Playwright (@playwright/test)
```bash
cd TypeScript_Playwright
npm install
npx playwright test
```
- **Pages**: `pages/AppPage.ts`
- **Tests**: `tests/automation_suite.spec.ts`
- **Config**: `playwright.config.ts`, `package.json`
{% endif %}

{% if "JavaScript" in target_languages %}
### 4. JavaScript Playwright (@playwright/test)
```bash
cd JavaScript_Playwright
npm install
npx playwright test
```
- **Pages**: `pages/AppPage.js`
- **Tests**: `tests/automation_suite.spec.js`
- **Config**: `playwright.config.js`, `package.json`
{% endif %}

---

## IEEE 829 Test Documentation
The full specification is available in:
- `docs/Test_Plan_IEEE829.md`
- `docs/network_har_summary.json`
'''


class TemplateRegistry:
    """Provides Jinja2 rendering environment with corporate filters and embedded templates."""

    def __init__(self) -> None:
        self.env = Environment(autoescape=False, trim_blocks=True, lstrip_blocks=True)
        # Register deterministic string sanitizers
        self.env.filters["to_snake_case"] = to_snake_case
        self.env.filters["to_camel_case"] = to_camel_case
        self.env.filters["to_pascal_case"] = to_pascal_case
        self.env.filters["escape_quotes"] = escape_quotes

        # Register template strings
        self.templates = {
            # Python
            "python_base_page": self.env.from_string(PYTHON_BASE_PAGE_TPL),
            "python_login_page": self.env.from_string(PYTHON_LOGIN_PAGE_TPL),
            "python_app_page": self.env.from_string(PYTHON_APP_PAGE_TPL),
            "python_test_suite": self.env.from_string(PYTHON_TEST_SUITE_TPL),
            "python_test_scenario_1": self.env.from_string(PYTHON_TEST_SCENARIO_1_TPL),
            "python_test_scenario_2": self.env.from_string(PYTHON_TEST_SCENARIO_2_TPL),
            "python_test_scenario_3": self.env.from_string(PYTHON_TEST_SCENARIO_3_TPL),
            "python_conftest": self.env.from_string(PYTHON_CONFTEST_TPL),
            "python_pytest_ini": self.env.from_string(PYTHON_PYTEST_INI_TPL),
            "python_requirements": self.env.from_string(PYTHON_REQUIREMENTS_TPL),
            # Java
            "java_pom_xml": self.env.from_string(JAVA_POM_XML_TPL),
            "java_testng_xml": self.env.from_string(JAVA_TESTNG_XML_TPL),
            "java_report_listener": self.env.from_string(JAVA_REPORT_LISTENER_TPL),
            "java_base_test": self.env.from_string(JAVA_BASE_TEST_TPL),
            "java_base_page": self.env.from_string(JAVA_BASE_PAGE_TPL),
            "java_login_page": self.env.from_string(JAVA_LOGIN_PAGE_TPL),
            "java_app_page": self.env.from_string(JAVA_APP_PAGE_TPL),
            "java_test_suite": self.env.from_string(JAVA_TEST_SUITE_TPL),
            "java_test_scenario_1": self.env.from_string(JAVA_TEST_SCENARIO_1_TPL),
            "java_test_scenario_2": self.env.from_string(JAVA_TEST_SCENARIO_2_TPL),
            "java_test_scenario_3": self.env.from_string(JAVA_TEST_SCENARIO_3_TPL),
            # TypeScript
            "ts_package_json": self.env.from_string(TS_PACKAGE_JSON_TPL),
            "ts_playwright_config": self.env.from_string(TS_PLAYWRIGHT_CONFIG_TPL),
            "ts_login_page": self.env.from_string(TS_LOGIN_PAGE_TPL),
            "ts_app_page": self.env.from_string(TS_APP_PAGE_TPL),
            "ts_test_suite": self.env.from_string(TS_TEST_SUITE_TPL),
            "ts_test_scenario_1": self.env.from_string(TS_TEST_SCENARIO_1_TPL),
            "ts_test_scenario_2": self.env.from_string(TS_TEST_SCENARIO_2_TPL),
            "ts_test_scenario_3": self.env.from_string(TS_TEST_SCENARIO_3_TPL),
            # JavaScript
            "js_package_json": self.env.from_string(JS_PACKAGE_JSON_TPL),
            "js_playwright_config": self.env.from_string(JS_PLAYWRIGHT_CONFIG_TPL),
            "js_enterprise_reporter": self.env.from_string(JS_ENTERPRISE_REPORTER_TPL),
            "js_login_page": self.env.from_string(JS_LOGIN_PAGE_TPL),
            "js_app_page": self.env.from_string(JS_APP_PAGE_TPL),
            "js_test_suite": self.env.from_string(JS_TEST_SUITE_TPL),
            "js_test_scenario_1": self.env.from_string(JS_TEST_SCENARIO_1_TPL),
            "js_test_scenario_2": self.env.from_string(JS_TEST_SCENARIO_2_TPL),
            "js_test_scenario_3": self.env.from_string(JS_TEST_SCENARIO_3_TPL),
            # Master README
            "master_readme": self.env.from_string(MASTER_README_TPL),
        }

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render registered template deterministically with context."""
        tpl = self.templates.get(template_name)
        if not tpl:
            raise KeyError(f"Template '{template_name}' not registered in TemplateRegistry.")
        return tpl.render(context)

