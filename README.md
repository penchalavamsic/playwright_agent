# Playwright Enterprise QA Agent Studio

Windows desktop tooling for executing explicit browser flows, capturing real evidence, and generating Python, Java, TypeScript and JavaScript Playwright projects. The Studio does not call an LLM or external AI API. It uses a deterministic flow grammar.

## Demo and complete guide

- [Watch or download the 88-second Full HD demo](demo_media/Playwright_Studio_Demo_Revised.mp4): the labeled application walkthrough with male narration, subtitles, real browser footage, reports, and login-loop diagnosis.
- [Read the complete application guide](documentation/output/Playwright_Studio_Complete_Guide.pdf): 34 pages covering everyday use and technical architecture, with 32 linked sections and nine diagrams.
- [Download the demo captions](demo_media/Playwright_Studio_Demo_Revised.srt).

The final media and guide use generic examples without personal or account details. Authoring requirements are in [the demo notes](demo_media/README.txt) and [the guide notes](documentation/README.txt). Raw captures, local credentials, saved browser state, and document-layout intermediates are excluded from version control.

## Run the corrected application

[Download the latest Windows build from GitHub Releases](https://github.com/penchalavamsic/playwright_agent/releases/latest).

Source: `.\.venv\Scripts\python main.py`

The verified Windows package is built separately under `dist_verified/PlaywrightEnterpriseQAStudio/`. Start `PlaywrightEnterpriseQAStudio.exe` there. Copy the **entire folder**, including `_internal`, to another machine. The older `dist_release` folder is not automatically updated.

The updated portable archive is `dist_verified/PlaywrightEnterpriseQAStudio-deployed-ready.zip`. It includes the simplified UI and deployed-site session controls. Extract it completely before starting the executable.

Install Edge or Chrome on the target machine. The Studio package includes the Playwright driver and available FFmpeg runtime. Missing video support is reported as unavailable; a fake recording is never substituted. Browser launch/policy errors are recorded as failures.

## Try a complete local flow

1. Click **Try demo**. This starts a disposable server on a free localhost port, loads the QA demo account, and fills the flow below.
2. Click **Run test**. Use **Advanced settings** to change languages or the output folder. Python scripts and a test plan are included by default.
3. Read the step outcomes in **Results**, or click **Open full report** for evidence. The primary flow should pass. The two additional advisory scenarios are **not run**, because generating a plan is not executing it.

The main screen contains only the URL, login profile, flow, and run controls. **Edit** beside the profile opens account setup. Browser/session options, script languages and the results folder are under **Advanced settings**. Logs and technical counters are in **Details**; the test plan and source files have their own tabs.

```text
Login as QA;
click "Tasks";
click "New task";
fill "Title" with "Office QA task";
select "High" from "Priority";
check "Notify team";
click "Create task";
verify API "/api/tasks" status code 201;
verify "Task created"
```

The demo account is `qa@example.test` / `local-demo-only`. It is only for this disposable local portal. The demo validates the title, priority, and checkbox values submitted to its API. It stores no real task data.

For a standalone portal, run `.\.venv\Scripts\python -m core.demo_portal` and visit `http://127.0.0.1:8765`.

## Writing flows

Separate steps with semicolons, newlines, or `and` / `then` before another action. Quote labels and values containing punctuation or conjunctions. Numbered lines are supported.

| Action | Example |
| --- | --- |
| Role login | `Login as ADMIN` |
| Click | `click "Reports"` |
| Fill | `fill "Email" with "qa@example.test"` |
| Type | `enter "Sample title" into "Title"` |
| Search and press Enter | `search for "Office QA task"` |
| Native select | `select "High" from "Priority"` |
| Checkbox | `check "Notify team"` / `uncheck "Notify team"` |
| Keyboard | `press "Enter"` |
| Navigate | `navigate to "/reports"` |
| Visibility | `verify "Task created"` |
| API status | `verify API "/api/tasks" status code 201` |

Controls must match a unique visible label, ID, test ID, name, or placeholder. The DOM is read again after each action. The browser stays in the current journey instead of returning to the starting page between clicks. API assertions use responses associated with the preceding action; a successful login request cannot satisfy a later failing request.

Unknown instructions, missing controls, ambiguous controls, failed login, and failed assertions fail the flow and skip dependent steps. They are not silently replaced with guessed actions. Arbitrary prose such as "test everything" is not supported. Custom dropdowns can be expressed as clicks; iframe traversal, popup switching, file uploads and arbitrary business assertions are not currently part of the automated grammar.

Use **Advanced settings → Manual browser session** for manual SSO/MFA and exploration, then **Capture and generate**. This records inspection evidence; it does **not** certify that the requested flow passed or reconstruct the manual journey. Review generated tests before relying on them.

## Deployed URLs and login loops

HTTP and HTTPS targets use the same flow runner. Start with **Advanced settings → Browser session → Fresh (incognito-like)** when a site works only in incognito. Each run gets a clean context, while every step within that run shares the same context and cookies.

Choose **Saved profile (normal)** when the application needs a remembered session. The Studio creates its own profile scoped to the target origin, role and browser; it does not use your personal browser profile. For saved sessions, set **Authenticated path** (for example `/dashboard`) or a CSS selector visible only after login. These markers verify the session before reusing it. Both markers must match if both are set. For SSO/MFA, use a saved profile in a manual browser session, sign in, capture and close the browser, then run the automated flow with the same project and role. Site-specific SSO behavior still needs validation against that site.

Login waits for delayed SPA forms and a stable authenticated page (2.5 seconds by default). A return to the login form fails the flow and skips dependent steps; the runner does not repeatedly submit credentials. It also checks for session loss between flow actions. The report includes sanitized navigation paths and HTTP 401/403 responses to help diagnose the redirect. The stability window is finite; it cannot guarantee a session will remain valid indefinitely.

Settings are saved in `browser-settings.json` and the workspace. Generated Python, JavaScript, TypeScript and Java suites apply the same session policy, each with a separate local profile directory. Do not run concurrent processes against one saved profile. `.browser_profiles/` contains authentication state and is excluded from version control.

CLI settings: `--session-mode fresh|persistent`, `--auth-success-path /dashboard`, `--auth-success-selector "[data-testid=account-menu]"`, `--auth-timeout 15`, and `--auth-settle 2.5` (times in seconds).

Session isolation cannot repair a deployed application's cookie domain/SameSite configuration, expired tokens, redirect configuration, or SSO policies. A failing target is reported instead of being marked passed. Local HTTP/HTTPS fixtures exercise these session controls; the office URL has not yet been supplied for direct verification.

## Accounts and projects

Save role accounts in the desktop profile panel. Selecting a role inserts login after initial navigation unless the flow already specifies login. Generated login actions preserve their recorded role; credentials come from the project's `.env`.

Open an existing project to append numbered runs. Previous inspection cases and numbered flow scripts remain available. Framework configurations execute numbered flow files, excluding the old canned aggregate/sanity files.

`.env` contains plaintext secrets and `.qa_studio_project.json` contains Base64-encoded passwords. Base64 is encoding, not encryption. Both files are gitignored in generated projects. Do not share them with reports. Screenshots, videos, and traces capture application content and should be handled as test evidence.

## Reports and generated suites

The Studio writes `Complete-Suite-Test-Report/index.html` and `report-summary.json` under each output project. Only the primary flow has execution results. Advisory UI/API plans are marked `not_run`. Durations, failures, final route, screenshots, recordings and traces come from the real run. Missing evidence is shown as unavailable.

Each generated language writes its own timestamped `execution-reports/<run>/` folder. Executing a generated suite never overwrites the Studio's inspection report or another language's report. Copy a report folder with its evidence subfolder for offline viewing.

Dependency installation is a separate initial provisioning step for generated projects. For an offline office machine, provision/cache the Python, Node or Maven dependencies first. The Studio executable does not include all four language toolchains.

```powershell
# From Python_Playwright
python -m pip install -r requirements.txt
python -m pytest

# From TypeScript_Playwright or JavaScript_Playwright
npm install
npm test

# From Java_Playwright (JDK 17+ and Maven)
mvn test
```

Set `BROWSER_CHANNEL=chrome` to use Chrome. JavaScript, TypeScript and Java default to Edge. Python tries Edge, Chrome, then bundled Chromium. Configure `BASE_URL` in the generated project's `.env`.

CLI use: `.\.venv\Scripts\python main.py --cli --url http://localhost:8765 --flow 'Login as QA; click "Tasks"' --profile QA --output PATH_TO_EXISTING_PROJECT`

CLI exit code is zero only when the flow passed. A generated report does not imply a successful test.

## Development and verification

```powershell
.\.venv\Scripts\python -m pip install -r requirements-dev.txt
.\.venv\Scripts\python -u -m unittest tests.test_flow_regressions tests.test_generated_execution tests.test_desktop tests.test_report_ui -v
npm install --prefix tmp/js_runtime @playwright/test dotenv typescript @types/node
.\.venv\Scripts\python -u -m unittest tests.test_other_languages tests.test_java -v
.\.venv\Scripts\python -u -m unittest tests.test_deployed_auth tests.test_generated_sessions -v
# After rebuilding the executable:
.\.venv\Scripts\python -u -m unittest tests.test_packaged tests.test_report_ui -v
```

`tests.test_generated_execution` creates passing/failing sample projects and records their location in `tmp/latest_verification.txt`. Cross-language checks use that project. The Java check uses the local Maven wrapper cache. Generated sample failures are intentional: the regression check passes only when these failures are correctly reported.

Historical `test_phase*.py` scripts test the former probe-based behavior, including placeholder evidence assumptions; the current regression suite is under `tests/`.

Build without replacing the older release:

```powershell
.\.venv\Scripts\python -m PyInstaller PlaywrightEnterpriseQAStudio.spec --noconfirm --distpath dist_verified --workpath build/verified
```

## Implementation

- `core/flow_parser.py`: explicit ordered grammar; preserves unsupported instructions.
- `core/flow_executor.py`: live control resolution, actions, assertions and per-step outcomes.
- `core/browser_inspector.py`: browser lifecycle, login, DOM, network and real media capture.
- `core/browser_session.py`: fresh/saved profiles, stable login checks and sanitized authentication diagnostics.
- `agents/`: parsing, inspection, advisory planning and scaffolding pipeline.
- `scaffolder/flow_codegen.py`: emits the actual flow for all four languages.
- `scaffolder/runtime_pytest.py` and `scaffolder/java_runtime/`: generated execution/report lifecycle.
- `scaffolder/runtime_auth.py` and `scaffolder/runtime_session.js`: generated authentication/session checks.
- `core/report_generator.py`: offline inspection report with evidence-backed statuses.
- `core/demo_portal.py`: self-contained local test application.
- `gui/app_window.py`: desktop interface and accurate execution outcome display.

See `VALIDATION.md` for findings and verification details. Use the complete application guide linked above for current procedures and architecture. The earlier architecture PDF describes the original design.
