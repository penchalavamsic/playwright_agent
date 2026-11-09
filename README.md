# Offline Playwright Enterprise QA Agent Studio

A **100% Offline, Zero-API Windows Desktop Agent** that deterministically inspects web applications and synthesizes complete corporate Page Object Model (POM) automation suites in **Python**, **Java**, **TypeScript**, and **JavaScript** alongside comprehensive **IEEE 829 Standard Test Plans**.

---

## 🌟 Key Corporate Architectural Features

- **100% Offline & Zero-API**: Zero external LLM API calls, zero cloud dependencies, and zero local model weights. Everything executes via deterministic rule-based algorithms and AST/Jinja2 synthesis.
- **Enterprise Browser Re-use**: Communicates directly with the workstation's pre-installed Google Chrome (`channel="chrome"`) or Microsoft Edge (`channel="msedge"`), eliminating external binary downloads.
- **Real-Time Telemetry & Safe Probing**: Discovers all interactive DOM controls using corporate locator prioritization (`data-testid` &rarr; `id` &rarr; `role + name` &rarr; `placeholder` &rarr; `label` &rarr; `text` &rarr; `css`) while intercepting XHR/Fetch network contracts and HTTP status codes (`200`, `201`, `400`, `401`, `403`, `500`).
- **5-Node LangGraph State Machine**: Deterministic stateful pipeline:
  `START` &rarr; `IntentParser` &rarr; `BrowserInspector` &rarr; `TestPlanner` &rarr; `CodeSynthesizer` &rarr; `ProjectScaffolder` &rarr; `END`.
- **CustomTkinter Desktop GUI**: Modern 60fps dark-themed interface with thread-safe `queue.Queue` streaming, 5-node visual progress cards, live counters, and multi-tab output inspector.
- **Self-Contained Standalone Executable**: Packaged into a portable Windows `.exe` (`dist/PlaywrightEnterpriseQAStudio/PlaywrightEnterpriseQAStudio.exe`) via PyInstaller.

---

## 🏗️ Architecture & Module Organization

```
playwright_agent/
│
├── core/                                # Phase 1: Browser Telemetry Engine
│   ├── models.py                        # Pydantic models (DOMElement, CapturedAPI, InspectionReport)
│   └── browser_inspector.py             # Playwright DOM inspection & safe network probing engine
│
├── agents/                              # Phase 2 & 3: LangGraph Pipeline Nodes
│   ├── state.py                         # AgentState TypedDict, ParsedFlowStep, TestScenarioSpec
│   ├── intent_parser.py                 # IntentParserNode (Rule-based NLP flow tokenizer)
│   ├── planner_node.py                  # TestPlannerNode (IEEE 829 Test Plan generator)
│   ├── code_synthesizer_node.py         # CodeSynthesizerNode & ProjectScaffolderNode
│   └── workflow_graph.py                # 5-node StateGraph pipeline definition
│
├── scaffolder/                          # Phase 3: Multi-Language Code Scaffolder
│   ├── template_registry.py             # Jinja2 environment with safe identifier filters
│   └── project_builder.py               # Multi-language corporate project directory builder
│
├── gui/                                 # Phase 4: Desktop Studio GUI
│   └── app_window.py                    # CustomTkinter Enterprise QA Agent Studio
│
├── main.py                              # Desktop Application & CLI Entry Point
├── build_exe.py                         # Automated PyInstaller packaging script
├── PlaywrightEnterpriseQAStudio.spec    # PyInstaller distribution specification
├── requirements.txt                     # Dependencies
│
├── test_phase1.py                       # Phase 1 verification harness
├── test_phase2.py                       # Phase 2 verification harness
├── test_phase3.py                       # Phase 3 verification harness
├── test_phase4.py                       # Phase 4 verification harness
└── test_phase5.py                       # Phase 5 smoke test verification harness
```

---

## 🚀 Quickstart Guide

### 1. Launching the Windows Desktop GUI
Run the compiled standalone executable directly (no Python needed):
```powershell
& "E:\MySpace\playwright_agent\dist\PlaywrightEnterpriseQAStudio\PlaywrightEnterpriseQAStudio.exe"
```
Or run directly from the Python virtual environment:
```powershell
.\.venv\Scripts\python.exe main.py
```

### 2. Running in Headless CLI Mode
```powershell
.\.venv\Scripts\python.exe main.py --cli --url "http://localhost:3000" --flow "Search for 'user', click dashboard, and verify 200 status code" --output "./my_test_suite"
```

---

## 🧪 Comprehensive Verification Suites

All 5 phases include dedicated automated test suites that run 100% offline against an embedded test portal:

```powershell
# Phase 1: Browser Inspector & DOM Telemetry
.\.venv\Scripts\python.exe test_phase1.py

# Phase 2: LangGraph State Machine & IEEE 829 Planner
.\.venv\Scripts\python.exe test_phase2.py

# Phase 3: Multi-Language POM Code Synthesizer (Python, Java, TS, JS)
.\.venv\Scripts\python.exe test_phase3.py

# Phase 4: CustomTkinter Desktop GUI & Queue Polling
.\.venv\Scripts\python.exe test_phase4.py

# Phase 5: Standalone PyInstaller Executable Smoke Test
.\.venv\Scripts\python.exe test_phase5.py
```

---

## 📁 Generated Deliverables Structure

When the pipeline executes, it generates a complete corporate directory hierarchy:

```
output_workspace/
│
├── docs/
│   ├── Test_Plan_IEEE829.md             # Formal IEEE 829 Corporate Test Plan
│   └── network_har_summary.json         # Captured API telemetry & status codes
│
├── README.md                            # Multi-framework execution manual
│
├── Python_Playwright/                   # pytest-playwright POM Framework
│   ├── pages/ (base_page.py, app_page.py)
│   ├── tests/ (test_automation_suite.py)
│   ├── conftest.py, pytest.ini, requirements.txt
│
├── Java_Playwright/                     # JUnit 5 / TestNG + Maven Framework
│   ├── pom.xml, testng.xml
│   └── src/ (BasePage.java, AppPage.java, AutomationSuiteTest.java)
│
├── TypeScript_Playwright/               # @playwright/test TypeScript Framework
│   ├── package.json, playwright.config.ts
│   ├── pages/ (AppPage.ts)
│   └── tests/ (automation_suite.spec.ts)
│
└── JavaScript_Playwright/               # @playwright/test JavaScript Framework
    ├── package.json, playwright.config.js
    ├── pages/ (AppPage.js)
    └── tests/ (automation_suite.spec.js)
```

