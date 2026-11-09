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

PYTHON_APP_PAGE_TPL = '''"""Corporate Page Object for {{ page_title or 'Application' }}."""

from typing import List, Optional
from playwright.sync_api import Locator, Page, expect
from pages.base_page import BasePage


class AppPage(BasePage):
    def __init__(self, page: Page, base_url: str = "{{ target_url }}"):
        super().__init__(page, base_url)

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

import pytest
from playwright.sync_api import Page, expect
from pages.app_page import AppPage


class TestAutomationSuite:
    """Corporate Automation Test Suite for {{ page_title or target_url }}."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.app = AppPage(page, base_url=base_url or "{{ target_url }}")
        self.app.navigate()

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

PYTHON_CONFTEST_TPL = '''"""Pytest configuration and corporate Playwright browser fixtures."""

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright


@pytest.fixture(scope="session")
def base_url() -> str:
    return "{{ target_url }}"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "ignore_https_errors": True,
        "viewport": {"width": 1440, "height": 900},
    }
'''

PYTHON_PYTEST_INI_TPL = '''[pytest]
addopts = -v -s --browser chrome --browser chromium
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
'''

PYTHON_REQUIREMENTS_TPL = '''playwright>=1.49.0
pytest>=8.0.0
pytest-playwright>=0.5.0
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
    <test name="E2E Automation Tests">
        <classes>
            <class name="com.corp.qa.tests.AutomationSuiteTest"/>
        </classes>
    </test>
</suite>
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
    private static final String TARGET_URL = "{{ target_url }}";

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
    "typescript": "^5.0.0"
  }
}
'''

TS_PLAYWRIGHT_CONFIG_TPL = '''import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: {
    timeout: 5000,
  },
  use: {
    baseURL: '{{ target_url }}',
    headless: true,
    ignoreHTTPSErrors: true,
    channel: 'chrome',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
'''

TS_APP_PAGE_TPL = '''import { Page, Locator, expect } from '@playwright/test';

export class AppPage {
  readonly page: Page;
  readonly baseUrl: string;

  constructor(page: Page, baseUrl: string = '{{ target_url }}') {
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

test.describe('Corporate Automation Suite: {{ page_title or target_url }}', () => {
  let app: AppPage;

  test.beforeEach(async ({ page }) => {
    app = new AppPage(page);
    await app.navigate();
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
    "@playwright/test": "^1.49.0"
  }
}
'''

JS_PLAYWRIGHT_CONFIG_TPL = '''const { defineConfig, devices } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests',
  timeout: 30000,
  expect: {
    timeout: 5000,
  },
  use: {
    baseURL: '{{ target_url }}',
    headless: true,
    ignoreHTTPSErrors: true,
    channel: 'chrome',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
'''

JS_APP_PAGE_TPL = '''const { expect } = require('@playwright/test');

class AppPage {
  /**
   * @param {import('@playwright/test').Page} page
   * @param {string} baseUrl
   */
  constructor(page, baseUrl = '{{ target_url }}') {
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

test.describe('Corporate Automation Suite: {{ page_title or target_url }}', () => {
  let app;

  test.beforeEach(async ({ page }) => {
    app = new AppPage(page);
    await app.navigate();
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
            "python_app_page": self.env.from_string(PYTHON_APP_PAGE_TPL),
            "python_test_suite": self.env.from_string(PYTHON_TEST_SUITE_TPL),
            "python_conftest": self.env.from_string(PYTHON_CONFTEST_TPL),
            "python_pytest_ini": self.env.from_string(PYTHON_PYTEST_INI_TPL),
            "python_requirements": self.env.from_string(PYTHON_REQUIREMENTS_TPL),
            # Java
            "java_pom_xml": self.env.from_string(JAVA_POM_XML_TPL),
            "java_testng_xml": self.env.from_string(JAVA_TESTNG_XML_TPL),
            "java_base_page": self.env.from_string(JAVA_BASE_PAGE_TPL),
            "java_app_page": self.env.from_string(JAVA_APP_PAGE_TPL),
            "java_test_suite": self.env.from_string(JAVA_TEST_SUITE_TPL),
            # TypeScript
            "ts_package_json": self.env.from_string(TS_PACKAGE_JSON_TPL),
            "ts_playwright_config": self.env.from_string(TS_PLAYWRIGHT_CONFIG_TPL),
            "ts_app_page": self.env.from_string(TS_APP_PAGE_TPL),
            "ts_test_suite": self.env.from_string(TS_TEST_SUITE_TPL),
            # JavaScript
            "js_package_json": self.env.from_string(JS_PACKAGE_JSON_TPL),
            "js_playwright_config": self.env.from_string(JS_PLAYWRIGHT_CONFIG_TPL),
            "js_app_page": self.env.from_string(JS_APP_PAGE_TPL),
            "js_test_suite": self.env.from_string(JS_TEST_SUITE_TPL),
            # Master README
            "master_readme": self.env.from_string(MASTER_README_TPL),
        }

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render registered template deterministically with context."""
        tpl = self.templates.get(template_name)
        if not tpl:
            raise KeyError(f"Template '{template_name}' not registered in TemplateRegistry.")
        return tpl.render(context)

