# Offline Playwright Enterprise QA Agent Studio

A **100% Offline, Zero-API Windows Desktop Agent** that deterministically inspects live web applications, captures real screenshots, screen recordings (`.webm`), and Playwright traces (`trace.zip`), and synthesizes complete corporate Page Object Model (POM) automation suites in **Python**, **Java**, **TypeScript**, and **JavaScript** alongside **IEEE 829 Standard Test Plans** and **Self-Contained Enterprise Test Evidence Reports**.

---

## 🌟 Key Corporate Architectural Features

- **100% Offline & Zero-API**: Zero external LLM API calls, zero cloud dependencies, zero external CDN links in generated reports, and zero local model weights. Everything runs locally on the Windows workstation via deterministic rule-based parsing and Jinja2 synthesis.
- **Enterprise Browser Re-use & Bundled Media Runtime**: Connects directly to pre-installed Microsoft Edge (`channel="msedge"`) or Google Chrome (`channel="chrome"`), with Playwright's driver and `ffmpeg` bundled into the `.exe` for offline `.webm` video recording.
- **Multi-Account `.env` & Role-Based Profile Switching (Phase 6)**:
  - Local credential vault stored in `<project_root>/.qa_studio_project.json` (Base64-encoded passwords) and written to `.env`, `.env.example`, `access-profiles.json`, and `.gitignore`.
  - Dynamic profile selection via GUI dropdown (`None (Public URL)`, `SUPER_USER`, `ADMIN`, `SUPER_USER_ADMIN_USER`, or any custom role) **or** automatic detection from user flow prompts (e.g., `"as super user..."`, `"login as admin..."`).
  - Automated login execution during live browser inspection and zero hardcoded usernames, passwords, tokens, or URLs in any generated script or test plan (`BASE_URL` and `TEST_ACCESS_PROFILE` resolved dynamically at runtime).
- **Timestamped & Multi-Day Persistent Workspaces**:
  - New runs automatically create `<Output_Folder>/<sanitized_domain>_<YYYY-MM-DD_HH-MM-SS>/` (e.g., `saucedemo_com_2026-11-21_14-32-42/`).
  - **📂 Open Existing Project** reloads an existing project's URL, saved role accounts, target languages, and sequential test counter (`001`, `002`, `003`, ...), appending new tests and IEEE 829 plan sections across multi-day runs without overwriting prior files.
- **Interactive Persistent Session Mode**: Supports manual two-step workflows (Step A: keep visible browser open for SSO/MFA/OTP/multi-page navigation &rarr; Step B: capture active DOM state, screenshots, video, trace, and generate suites).
- **Self-Contained Enterprise Test Evidence Reporting (Phase 7)**:
  - Generates `Complete-Suite-Test-Report/index.html` with inline CSS/JS (zero external CDNs), executive KPI cards, filter/search controls, step-by-step screenshots, playable `video.webm` screen recordings, downloadable `trace.zip`, captured API status matrices, and per-test IEEE 829 plans.
  - Dynamically resolves the target application name and domain (zero hardcoded app names).
  - Embeds native screenshot, video, and report generation into all 4 generated Playwright frameworks (`conftest.py` for Python, `BaseTest.java` + `EnterpriseReportListener.java` for Java/TestNG, and `enterprise-reporter.js` for TypeScript/JavaScript).
- **5-Node LangGraph State Machine**:
  `START` &rarr; `IntentParser` &rarr; `BrowserInspector` &rarr; `TestPlanner` &rarr; `CodeSynthesizer` &rarr; `ProjectScaffolder` &rarr; `END`.
- **CustomTkinter Desktop GUI**: Dark-themed desktop interface with thread-safe `queue.Queue` streaming, 5-node visual pipeline cards, live telemetry counters, **📂 Open Existing Project**, **🔑 Role-Based Access Profiles (.env)** vault, **📊 Open Test Report** launcher, and multi-tab output previewer.
- **Standalone Windows Executable**: Packaged into `dist_release/PlaywrightEnterpriseQAStudio/PlaywrightEnterpriseQAStudio.exe` via PyInstaller.

---

## 🏗️ Architecture & Module Organization

```
playwright_agent/
│
├── core/                                # Core Telemetry, Persistence & Reporting
│   ├── models.py                        # Pydantic models (DOMElement, CapturedAPI, InspectionReport)
│   ├── browser_inspector.py             # Playwright DOM inspector, auto-login, screenshots, video & trace capture
│   ├── workspace_manager.py             # Phase 6: Multi-day .qa_studio_project.json, .env, access-profiles.json, domain+timestamp folders
│   └── report_generator.py              # Phase 7: Self-contained offline Complete-Suite-Test-Report generator
│
├── agents/                              # LangGraph Deterministic Pipeline Nodes
│   ├── state.py                         # AgentState TypedDict, ParsedFlowStep, TestScenarioSpec
│   ├── intent_parser.py                 # IntentParserNode (Flow NLP tokenizer, role detector & output dir resolver)
│   ├── planner_node.py                  # TestPlannerNode (Append-safe IEEE 829 Test Plan generator)
│   ├── code_synthesizer_node.py         # CodeSynthesizerNode & ProjectScaffolderNode
│   └── workflow_graph.py                # 5-node StateGraph pipeline definition
│
├── scaffolder/                          # Multi-Language Code Scaffolder
│   ├── template_registry.py             # Jinja2 templates for Python, Java, TS, JS (LoginPage, BaseTest, reporters)
│   └── project_builder.py               # Multi-language corporate repository & evidence builder
│
├── gui/                                 # Desktop Studio GUI
│   └── app_window.py                    # CustomTkinter Studio (Project Loader, Role Vault, Interactive Mode, Report Launcher)
│
├── PLAN_TEMPLATE.md                     # Corporate IEEE 829 Test Plan template rules
├── main.py                              # Desktop Application & CLI Entry Point
├── build_exe.py                         # Automated PyInstaller packaging script (outputs to dist_release/)
├── PlaywrightEnterpriseQAStudio.spec    # PyInstaller spec (bundles Playwright driver & ffmpeg)
├── requirements.txt                     # Python dependencies
│
├── test_phase1.py                       # Phase 1: Browser Inspector & DOM Telemetry verification
├── test_phase2.py                       # Phase 2: LangGraph Pipeline & IEEE 829 Planner verification
├── test_phase3.py                       # Phase 3: Multi-Language POM Code Synthesizer verification
├── test_phase4.py                       # Phase 4: CustomTkinter Desktop GUI verification
├── test_interactive_mode.py             # Phase 4.1: Interactive Two-Step Session verification
├── test_phase5.py                       # Phase 5: Standalone Executable smoke test
├── test_phase6.py                       # Phase 6: Multi-Account .env & Multi-Day Workspace verification
└── test_phase7.py                       # Phase 7: Self-Contained Enterprise Reporting & Real Media verification
```

---

## 🚀 Quickstart Guide

### 1. Launching the Standalone Windows Desktop App
Run the compiled executable directly (no Python installation required):
```powershell
& "E:\MySpace\Projects\playwright_agent\dist_release\PlaywrightEnterpriseQAStudio\PlaywrightEnterpriseQAStudio.exe"
```
Or launch from the Python virtual environment:
```powershell
.\.venv\Scripts\python.exe main.py
```

### 2. Running in Headless CLI Mode
```powershell
.\.venv\Scripts\python.exe main.py --cli --url "https://www.saucedemo.com" --flow "Search for 'backpack', click 'Cart' and verify 200 status code" --output "./Test"
```

### 3. Rebuilding the Standalone `.exe`
```powershell
.\.venv\Scripts\python.exe build_exe.py
```
The compiled executable and bundled runtime are written to:
`dist_release\PlaywrightEnterpriseQAStudio\PlaywrightEnterpriseQAStudio.exe`

---

## 🧪 Verification Suites

```powershell
# Phase 1: Browser Inspector & DOM Telemetry
.\.venv\Scripts\python.exe test_phase1.py

# Phase 2: LangGraph State Machine & IEEE 829 Planner
.\.venv\Scripts\python.exe test_phase2.py

# Phase 3: Multi-Language POM Code Synthesizer (Python, Java, TS, JS)
.\.venv\Scripts\python.exe test_phase3.py

# Phase 4: CustomTkinter Desktop GUI & Queue Polling
.\.venv\Scripts\python.exe test_phase4.py

# Phase 4.1: Interactive Two-Step Persistent Browser Mode
.\.venv\Scripts\python.exe test_interactive_mode.py

# Phase 5: Standalone PyInstaller Executable Smoke Test
.\.venv\Scripts\python.exe test_phase5.py

# Phase 6: Multi-Account .env, Dynamic Role Selection & Multi-Day Persistence
.\.venv\Scripts\python.exe test_phase6.py

# Phase 7: Self-Contained Enterprise Reporting, Zero-Leak Sweep & Real Media Capture
.\.venv\Scripts\python.exe test_phase7.py
```

---

## 📁 Generated Deliverables Structure

Each new run creates a self-contained timestamped workspace inside the chosen output folder:

```
<Output_Folder>/<sanitized_domain>_<YYYY-MM-DD_HH-MM-SS>/
│
├── .env                                 # Local BASE_URL, TEST_ACCESS_PROFILE, and role credentials (gitignored)
├── .env.example                         # Safe placeholder template for Git sharing
├── .gitignore                           # Ignores .env, .qa_studio_project.json, caches, build artifacts
├── .qa_studio_project.json              # Local multi-day workspace state, sequence counter & encoded vault
├── access-profiles.json                 # Maps role names to environment variable keys
├── README.md                            # Multi-framework execution manual
│
├── Complete-Suite-Test-Report/          # Phase 7: 100% Offline Enterprise Test Evidence Report
│   ├── index.html                       # Self-contained HTML report (zero external CDNs)
│   ├── README.txt                       # Offline viewing instructions
│   ├── report-summary.json              # Machine-readable KPI & scenario summary
│   └── Evidence/
│       ├── Plans/<TEST_ID>/             # Per-test IEEE 829 markdown plans
│       ├── Screenshots/<TEST_ID>/       # Real step PNGs & final-screenshot.png
│       ├── Recording/<TEST_ID>/         # Playable Playwright video.webm
│       └── Trace/<TEST_ID>/             # Playwright trace.zip archive
│
├── docs/
│   ├── Test_Plan_IEEE829.md             # Master append-safe IEEE 829 Corporate Test Plan
│   └── network_har_summary.json         # Captured API telemetry & status codes
│
├── Python_Playwright/                   # pytest-playwright POM Framework + Report Hooks
│   ├── pages/ (base_page.py, login_page.py, app_page.py)
│   ├── tests/ (001_<flow>.py, test_automation_suite.py, test_ui_sanity_check.py, test_api_contract_matrix.py)
│   └── conftest.py, pytest.ini, requirements.txt
│
├── Java_Playwright/                     # TestNG + Maven Framework + EnterpriseReportListener
│   ├── pom.xml, testng.xml
│   └── src/
│       ├── main/java/com/corp/qa/pages/ (BasePage.java, LoginPage.java, AppPage.java)
│       └── test/java/com/corp/qa/
│           ├── listeners/ (EnterpriseReportListener.java)
│           └── tests/ (BaseTest.java, Test001<Flow>.java, AutomationSuiteTest.java, ...)
│
├── TypeScript_Playwright/               # @playwright/test TypeScript Framework + Custom Reporter
│   ├── package.json, playwright.config.ts, enterprise-reporter.js
│   ├── pages/ (LoginPage.ts, AppPage.ts)
│   └── tests/ (001_<flow>.spec.ts, automation_suite.spec.ts, ui_sanity_check.spec.ts, api_contract_matrix.spec.ts)
│
└── JavaScript_Playwright/               # @playwright/test JavaScript Framework + Custom Reporter
    ├── package.json, playwright.config.js, enterprise-reporter.js
    ├── pages/ (LoginPage.js, AppPage.js)
    └── tests/ (001_<flow>.spec.js, automation_suite.spec.js, ui_sanity_check.spec.js, api_contract_matrix.spec.js)
```
