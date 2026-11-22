"""Source content for the anonymous application manual."""
SECTIONS = []
def section(title, audience, blocks):
    SECTIONS.append(dict(title=title, audience=audience, blocks=blocks))
def p(t): return ('p', t)
def h(t): return ('h', t)
def steps(*items): return ('steps', items)
def bullets(*items): return ('bullets', items)
def table(headers, rows, widths=None): return ('table', headers, rows, widths)
def code(t): return ('code', t)
def fig(kind, caption): return ('figure', kind, caption)

section('Understanding the application', 'All readers', [
p('Playwright Studio is a Windows desktop application for checking browser workflows and producing reusable automation projects. You provide an application address, an optional login profile, and an ordered list of actions. The Studio opens a browser, attempts those actions, records the outcome, and prepares a report with the evidence it actually captured.'),
p('You can use the desktop interface without writing programming code. Developers can review and run the generated Python, Java, TypeScript, or JavaScript projects independently. These exported projects require their own language tools and dependencies.'),
h('Three outputs with different meanings'),
table(['Output', 'What it tells you'], [
['Executed flow', 'Whether the requested actions and checks passed in the browser during that run.'],
['Test plan', 'What should be tested. A planned scenario is not evidence that it ran.'],
['Generated project', 'Reusable source files for another execution. Creating files does not mean those files have already passed.']],[.27,.73]),
h('How the application makes decisions'),
p('The workflow is deterministic: explicit grammar, browser observations, and code templates drive its decisions. The application does not call a large language model or require an external AI API key. It does access the target web application and its network services; a deployed site still needs its normal network connection.'),
p('The word agent refers to the coordinated processing stages. It does not mean the application understands every natural-language request or can independently test an entire business process.'),
h('Reading this guide'),
p('Start with sections 2 to 14 for installation, daily use, and results. Sections 15 to 21 cover reuse, commands, and troubleshooting. Sections 22 to 29 explain internals and maintenance. Replace every angle-bracket placeholder, such as <TARGET_URL> or <ROLE>, with your own approved value before using an example. Product names, button labels, and source filenames identify real application components; example people, organizations, and accounts are not used.')
])

section('Installing and launching the Studio', 'All readers', [
h('Portable desktop installation'),
steps('Obtain the packaged application from your approved distribution location. Extract the archive into a folder where your account can read and write files.',
'Keep the complete application folder together, including the _internal directory. Start PlaywrightEnterpriseQAStudio.exe from the extracted folder.',
'Make sure Microsoft Edge or Google Chrome is installed and allowed to run. A local browser is required even when you choose background execution.',
'Choose a writable results folder. Make sure the target application is reachable from this machine, including any required network or VPN connection.',
'Launch the Studio and use Try demo for an initial check before configuring a deployed application.'),
table(['Component', 'Required for'],[
['Windows and the extracted package', 'Running the packaged desktop application. The portable build does not require a separate Python installation.'],
['Edge or Chrome', 'Browser execution. Bundled Chromium is only a fallback when it is installed.'],
['Writable storage', 'Projects, reports, screenshots, traces, video, and saved sessions.'],
['Python, Node.js, or Java tools', 'Running the corresponding exported project or working from source, not ordinary packaged desktop use.']],[.34,.66]),
h('Launching from source'),
code('python -m venv .venv\n.\\.venv\\Scripts\\python -m pip install -r requirements.txt\n.\\.venv\\Scripts\\python main.py'),
p('Run these commands from the source checkout with a compatible Python installation. The requirements file declares the Python dependencies. A separate Playwright browser download is unnecessary when an installed Edge or Chrome channel works. Internet access or a prepared package cache is needed for initial dependency provisioning.'),
p('If the window does not open, run the source command from a terminal to read the error. If browser launch fails, inspect the report and Details panel for the actual launch or policy error before changing the test flow.')
])

section('Completing the first successful run', 'All readers', [
p('The built-in demo provides a disposable local application, a prepared profile, and an example flow. It is the fastest way to verify the Studio installation without supplying a real application account.'),
fig('journey', 'Figure 1  The everyday workflow from setup to reusable results'),
steps('Open the Studio and select Try demo. Allow it to populate the application URL, profile, and flow. The local port is selected automatically.',
'Leave the default Python output and test plan enabled for the first attempt. Use Advanced settings only if you need another language or a different results folder.',
'Select Run test. Wait for the execution and report-generation stages to finish. Background mode runs the browser without showing its window.',
'Read Results. The demo flow should pass and show outcomes for its individual steps, including initial navigation.',
'Select Open full report. Expand the executed case and inspect its steps, screenshots, API results, and available recording or trace.',
'Open the Test plan and Files tabs. These show generated material; use the execution result to decide whether the actual run passed.'),
h('Expected interpretation'),
p('The primary demo flow executes. The additional advisory scenarios remain not run. A report containing an executed pass alongside unexecuted plans is therefore expected. Do not count the plans as additional passing tests.'),
h('Moving to your application'),
p('After the demo works, start a separate project for your application. Replace the local URL, select the correct account profile, and write a short flow with an explicit final assertion. The demo proves the local installation can run its fixture; it does not prove a deployed site or its sign-in policy will work.'),
p('The demonstration server stores no real business records. For an application under test, browser actions may create or change actual data. Use an appropriate test environment and test values.')
])

section('Finding your way around the interface', 'All readers', [
p('The main screen keeps setup controls on the left and results on the right. Open the optional account editor and advanced controls only when needed.'),
fig('interface', 'Figure 2  Labeled interface map with generic placeholders rather than live account data'),
table(['Area', 'Purpose'],[
['Open project and Try demo', 'Continue an existing workspace, or load the disposable demonstration.'],
['Application URL and login profile', 'Choose the target and the account role used for this test. Edit opens profile setup.'],
['Test flow', 'Describe the ordered actions and assertions. This is the main test input.'],
['Advanced settings', 'Choose session behavior, login markers, browser visibility, manual mode, languages, plan generation, and output location.'],
['Results and Details', 'Read step outcomes in Results. Use Details for logs, technical counters, and pipeline information.'],
['Test plan and Files', 'Review the generated plan and select a generated file to inspect.'],
['Report and folder controls', 'Open the full HTML report or the project output folder after generation.']],[.34,.66]),
p('Capture and generate is shown during a manual browser session. Close browser is available for the managed visible browser. These controls serve a different workflow from an automated Run test.')
])

section('Choosing an application and a project', 'All readers', [
h('Use the address that starts the intended journey'),
p('Enter the full HTTP or HTTPS address of the page where the test should begin. A local application must already be running unless you use Try demo. A deployed application must be reachable with the same network access available to the Studio process. Using an explicit scheme avoids ambiguity between local HTTP and deployed HTTPS.'),
p('The runner inserts initial navigation to the target URL. Relative navigation steps later in the flow are resolved against that configured target URL. Use a full address when crossing to another origin is deliberate; a different origin can also change which saved profile is appropriate.'),
h('Start a new project'),
steps('Select the application URL and write the flow.', 'Choose an output base folder in Advanced settings. A new workspace is placed beneath it using an application-derived folder label and run suffix.', 'Save the needed login profile and select outputs.', 'Run the flow and use Open results folder to locate the actual project root.'),
h('Continue an existing project'),
steps('Select Open project and choose the folder containing .qa_studio_project.json.', 'Confirm the loaded target URL, profile, languages, and browser settings.', 'Enter the next flow and run it. The project advances its sequence number and retains earlier numbered flows and report cases.'),
table(['Situation', 'Project choice'],[
['Another flow for the same application and test context', 'Reopen the existing project and review its stored configuration.'],
['Different application or unrelated test environment', 'Use a separate workspace to keep configuration and evidence clear.'],
['Need to reproduce a previous result', 'Keep the original evidence and record the relevant flow and configuration before a new run.']],[.48,.52]),
p('A project is more than its HTML report. It also contains configuration, stored accounts, source files, and history. Sharing only a report is different from sharing the entire workspace; see sections 15 and 28.')
])

section('Configuring login profiles', 'All readers', [
p('A profile associates a role label with a username and password. The role describes the access level needed by a flow; it is not the name of a person. Public pages can use None (Public URL) without an account.'),
steps('Choose the required role in the login profile control. Select Edit to open account setup.', 'Enter the role label, username or email, and password for the approved test account. Select Save profile.', 'Select that profile for the run. Check that the credentials belong to the target environment.', 'For an explicit login step, use Login as <ROLE>, replacing <ROLE> with the saved role label. Follow it with the application actions and a meaningful assertion.'),
h('How profile selection affects the flow'),
p('If a non-public profile is selected and the flow contains no login instruction, the parser inserts a login step after initial navigation. If the flow includes login, its role is preserved. Keep the selected role and written login role consistent to make the result easy to interpret.'),
p('Role labels are normalized to uppercase with separators converted to underscores. Generated projects obtain account values from environment-variable mappings rather than embedding the username and password in each test action.'),
code('Login as <ROLE>;\nverify "<SIGNED_IN_LABEL>";\nclick "<TARGET_BUTTON>";\nverify "<EXPECTED_RESULT>"'),
h('Credential storage'),
p('The project .env file contains plaintext credentials. The workspace JSON stores passwords encoded with Base64, which is reversible and is not encryption. The generated ignore file excludes both files and saved browser profiles from ordinary version control, but it does not protect copies, backups, screenshots, or manual uploads.'),
p('The access-profiles.json file maps roles to environment-variable names. It is not a credential vault. Keep real account values local, and remove them from any material being shared. Update both the selected profile and the environment configuration when an account changes.'),
p('Automated form login supports common username and password forms. Unusual multi-stage login, identity-provider redirects, or MFA may require manual sign-in and a saved session; section 11 explains that procedure.')
])

section('Writing a clear test flow', 'All readers', [
p('Write a sequence of small, observable actions. Each instruction should identify one action and one target. Finish with a check that expresses the result you actually care about, rather than stopping immediately after a click.'),
h('Use explicit boundaries'),
p('Separate steps with semicolons or newlines. Numbered lines are accepted. The parser also recognizes conjunctions such as and or then before another action, but semicolons are easier to review. Put labels and input values in double quotes, especially when they contain punctuation or words such as and.'),
code('click "<SECTION_LABEL>";\nclick "<CREATE_BUTTON>";\nfill "<FIELD_LABEL>" with "<TEST_VALUE>";\nclick "<SUBMIT_BUTTON>";\nverify "<CONFIRMATION_TEXT>"'),
h('Match the application rather than describing an intention'),
p('A target should uniquely identify a visible control by its label, test ID, ID, name, or placeholder. The runner refreshes its view of the page after each action, so controls revealed by a previous click can be used next. If two controls share the same target, use a stable unique identifier supplied by the application.'),
table(['Less useful request', 'Reviewable replacement'],[
['Test the whole page', 'List the specific actions and final conditions to check.'],
['Make sure saving works', 'Fill the required fields, click the save control, and verify a visible confirmation or API status.'],
['Click the button', 'Use the unique visible label or test identifier of the intended control.'],
['Wait for everything', 'Use supported actions and observable assertions. Arbitrary wait instructions are not supported.']],[.36,.64]),
h('Put API checks next to their cause'),
p('Place an API assertion immediately after the action that causes the request. The runner checks captured responses associated with the preceding non-assertion action. An unrelated successful login response must not be used as evidence that a later save succeeded.'),
p('The grammar is intentionally limited. Unknown instructions remain in the flow and fail visibly; they are not silently removed or converted into guessed actions.')
])

section('Supported action reference', 'Users and developers', [
p('Replace placeholders before execution. Text inside quotation marks should match your application. The action names below describe the automated grammar, not everything a person can do in manual browser mode.'),
table(['Action', 'Template and behavior'],[
['Login', 'Login as <ROLE>\nUse the configured role and verify a stable authenticated state.'],
['Click', 'click "<LABEL>"\nActivate a unique visible button, link, tab, or supported clickable control.'],
['Fill or enter', 'fill "<FIELD>" with "<VALUE>"\nAlternative: enter "<VALUE>" into "<FIELD>".'],
['Search', 'search for "<QUERY>"\nFind a search input, fill it, and press Enter.'],
['Select', 'select "<OPTION>" from "<FIELD>"\nChoose by label from a native HTML select control.'],
['Check or uncheck', 'check "<CHECKBOX>"\nuncheck "<CHECKBOX>" sets an explicit checkbox state.'],
['Keyboard', 'press "<KEY>"\nSend a key to the currently focused page control.'],
['Navigate', 'navigate to "<PATH_OR_URL>"\nVisit an address; a relative path uses the configured target as its base.'],
['Verify visible UI', 'verify "<EXPECTED_TEXT>"\nAssert that the uniquely resolved target or exact text is visible.'],
['Verify API status', 'verify API "<ENDPOINT_FRAGMENT>" status code <CODE>\nRequire matching observed responses from the preceding action to have accepted status codes.']],[.24,.76]),
p('For API assertions, use a concrete expected HTTP status such as 200 for a successful read or the status documented for your operation. If no status is written, the parser uses 200, 201, and 204. An explicit endpoint fragment and status make the check more precise.'),
p('A custom dropdown may need a click on its opener followed by a click on an option. The select instruction is for native select elements. Visibility checks do not compare arbitrary field values, database state, calculations, or response-body business rules.')
])

section('Adapting example flows', 'All readers', [
h('Public page navigation'),
code('click "<NAVIGATION_LINK>";\nverify "<DESTINATION_HEADING>"'),
p('Choose None (Public URL). Replace the link and heading with unique visible text. This small flow is useful for separating navigation problems from authentication problems.'),
h('Authenticated record creation'),
code('Login as <ROLE>;\nclick "<RECORDS_SECTION>";\nclick "<CREATE_BUTTON>";\nfill "<TITLE_FIELD>" with "<UNIQUE_TEST_VALUE>";\nselect "<OPTION_LABEL>" from "<SELECT_FIELD>";\ncheck "<CHECKBOX_LABEL>";\nclick "<SAVE_BUTTON>";\nverify API "<ENDPOINT_FRAGMENT>" status code <CODE>;\nverify "<SUCCESS_MESSAGE>"'),
p('Use values permitted in your test environment. This pattern checks browser interaction, the corresponding HTTP outcome, and visible confirmation. It does not automatically verify every submitted value in the server database. Add those business checks in the exported suite if required.'),
h('Search and review'),
code('Login as <ROLE>;\nclick "<SEARCH_SECTION>";\nsearch for "<QUERY>";\nverify "<EXPECTED_RESULT_TEXT>"'),
p('Search fills the identified search input and presses Enter. If multiple search fields are visible, use fill with a unique field label followed by press "Enter" instead. Make sure the expected result exists before the run.'),
h('Prepare repeatable data'),
p('A successful creation flow can leave a new record behind. Reusing the same unique value may fail on a later run even when the application behaves correctly. Prepare fresh data, reset the test environment, or add a reviewed cleanup step in custom automation. The Studio does not automatically undo business actions.'),
p('Placeholders are documentation notation, not variables that the flow parser automatically expands. Replace all of them with real labels, roles, paths, values, and numeric status codes before selecting Run test.')
])

section('Choosing browser session behavior', 'All readers', [
p('Open Advanced settings to choose how the browser handles saved state. Session mode and browser visibility are separate choices: a fresh or saved session can run in the background, while manual interaction requires a visible browser.'),
table(['Mode', 'What it does', 'When to use it'],[
['Fresh (incognito-like)', 'Creates a clean context for the run. All steps in that run share its cookies and state.', 'A repeatable clean start, especially when the application works only in incognito.'],
['Saved profile (normal)', 'Uses a dedicated local profile for the project, origin, role, and browser.', 'Remembered authentication or a prepared session that must survive between runs.']],[.27,.38,.35]),
h('Configure a reliable success marker'),
steps('Identify a path reached only after login, or a CSS selector visible only to an authenticated user.', 'Enter it in Authenticated path or Logged-in CSS selector. If you supply both, both must match.', 'Run a short login and visibility check before trying a long workflow.', 'Inspect the result and diagnostics. Do not treat the brief appearance of a dashboard as proof that the session is stable.'),
code('Authenticated path: <SIGNED_IN_PATH>\nLogged-in CSS selector: <AUTHENTICATED_SELECTOR>'),
p('A saved session without a visible login form requires a success marker before it can be accepted. A path marker matches the specified path or a nested path segment; a selector should identify a stable authenticated control, not an element also present on the login page.'),
h('Important distinctions'),
p('Saved mode uses the Studio project profile, not your personal Edge or Chrome profile. Closing and reopening the same project with the same origin, role, and browser preserves that identity. Changing one of those inputs can select another profile.'),
p('Do not run simultaneous processes against the same saved profile. Close an existing managed session before starting another. A clean context can remove stale local state from the test, but it cannot repair the deployed application\'s session or redirect logic.')
])

section('Using manual sign in and capture', 'All readers', [
p('Manual browser mode lets a person complete steps the automated grammar cannot handle, such as an interactive identity-provider challenge. It captures inspection evidence from the resulting browser state. It does not replay or certify the manual journey.'),
fig('manual', 'Figure 3  Preparing a saved session and then running a separate automated check'),
steps('Open or create the intended project. Select the role and Saved profile (normal) when you want the session to be reusable.', 'Set a reliable authenticated path or selector. Enable Manual browser session; the browser becomes visible.', 'Select Run test to open the browser. Complete the required sign-in or manual navigation in that browser.', 'Select Capture and generate after the desired state is ready. Review the captured state and generated output.', 'Close the managed browser. Turn off Manual browser session and run an explicit automated flow using the same project, origin, role, and browser.', 'Confirm the automated run actually passes. If the saved session cannot be validated, diagnose its markers or repeat manual sign-in as appropriate.'),
h('What capture does and does not prove'),
p('Capture records the current inspected page, visible elements, network observations, and available media. There are no automated execution steps for that manual session, so its flow status is not_run. A visible signed-in page is useful inspection evidence, but it is not a passing automation result.'),
p('The Studio does not reconstruct every manual click into a reliable recorded script. Generated code must be reviewed and executed separately. Site-specific SSO or MFA behavior, including profile persistence and expiry, must be checked against the actual environment.')
])

section('Running a flow and interpreting outcomes', 'All readers', [
steps('Confirm the target, profile, flow, output folder, and browser mode.', 'Select Run test. The application validates required inputs and starts its processing pipeline.', 'Wait for completion, then read Results from the first step onward.', 'If a step failed, investigate that step before trying later skipped steps.', 'Open the report and preserve its evidence when reporting a problem.'),
fig('failure', 'Figure 4  The first failed step stops dependent actions'),
table(['Status', 'Interpretation'],[
['Passed', 'The attempted step or executed flow met its implemented checks. It does not prove unrelated requirements.'],
['Failed', 'An attempted action or assertion did not meet its condition, or execution could not complete. Read the error.'],
['Skipped', 'The action was not attempted because an earlier step failed. It is not a second independent failure.'],
['Not run', 'There is no execution result for this scenario, for example an advisory plan or manual inspection.']],[.22,.78]),
h('Progress is not a test result'),
p('A pipeline reaching its final stage means processing and file generation finished. A report may still describe a failed flow. The authoritative outcome is the execution status and its step details. Similarly, a large number of generated files or discovered elements does not indicate test coverage.'),
p('The runner keeps the same journey alive across actions instead of returning to the initial page between clicks. A login loop or lost session stops dependent actions rather than repeatedly submitting credentials. This preserves the failure for diagnosis.')
])

section('Reading the complete report', 'All readers', [
p('Select Open full report after a run, or open Complete-Suite-Test-Report/index.html from the project folder. The report is a local HTML document with related evidence files. Keep its directory structure intact when moving it.'),
steps('Read the summary counts and browser/profile context.', 'Use the status filters to focus on passed, failed, or unexecuted cases.', 'Expand a case and read its purpose, steps, actual result, error, and measured duration.', 'Check that the evidence belongs to the case and action being discussed.', 'Compare the outcome with the requested flow, then decide whether to fix the flow, environment, or application.'),
h('Understand the pass rate'),
p('The Studio report calculates pass rate from executed passed and failed cases: passed divided by passed plus failed, multiplied by 100. Not-run and skipped cases are excluded. If there are no executed cases, the displayed pass rate is zero.'),
table(['Illustrative count', 'Meaning'],[
['1 passed, 0 failed, 2 not run', 'One executed case passed. The pass rate is 100 percent of executed cases, not proof that three cases ran.'],
['0 passed, 1 failed, 2 not run', 'The executed flow failed. The additional plans remain unverified.'],
['0 passed, 0 failed, 3 not run', 'No executed result is available. Review why these are only planned or inspected cases.']],[.43,.57]),
h('Case counts and step counts differ'),
p('A single executed flow can contain many steps. The dashboard counts test cases; the expanded case explains the steps. Advisory UI and API scenarios can appear beside the primary flow but remain not_run until separately implemented and executed.'),
p('The report format includes a flaky category, but the Studio flow runner does not automatically retry the login flow or establish flakiness by repeated execution. Missing evidence is displayed as unavailable. An older report without trustworthy execution provenance is retained as not_run when migrated, rather than preserving an unsupported pass claim.'),
p('Reports normally contain operational dates and measured durations. This manual uses no captured dates or personal values in its examples; that presentation choice does not change the application\'s report data.')
])

section('Using screenshots video and traces', 'All readers', [
table(['Evidence', 'Best use', 'Limit'],[
['Step screenshot', 'See the visible state after an attempted action or assertion.', 'Shows one moment, not all hidden application state.'],
['Final screenshot', 'Review the final page or failure position.', 'Does not establish that every earlier requirement passed.'],
['Browser recording', 'Watch the sequence and a visible redirect or interaction problem.', 'May be unavailable if recording support or finalization failed.'],
['Playwright trace', 'Investigate browser actions and recorded snapshots in a trace viewer.', 'May contain application data and requires a compatible local viewer.'],
['API observations', 'Check the endpoint, status, method, and associated triggering action.', 'A successful HTTP status alone does not prove business correctness.'],
['Plan and summary JSON', 'Review intended checks or consume structured report data.', 'A plan is not execution evidence.']],[.25,.37,.38]),
h('Investigate a failed save'),
steps('Find the failed step in the expanded report case.', 'Read its error and inspect the nearest step screenshot.', 'Check the request associated with the preceding action if an API assertion failed.', 'Use the recording or trace to see whether navigation, authentication, or a hidden/ambiguous control changed the journey.', 'Record the observed result and expected result without inventing missing evidence.'),
h('Open a trace locally'),
code('python -m playwright show-trace "<TRACE_ZIP_PATH>"'),
p('Use this command in a Python environment where Playwright is installed. A JavaScript or TypeScript environment with the Playwright CLI can use npx playwright show-trace "<TRACE_ZIP_PATH>". Keep sensitive trace files in your approved local environment.'),
h('Share a usable evidence package'),
p('Copy the full report folder, including its Evidence subfolders, so relative links continue to work. Do not send only index.html and expect the recording, screenshots, or trace to travel with it. Review the content before sharing; screenshots and network traces can reveal real records or session information.')
])

section('Understanding the project files', 'Users and developers', [
p('The workspace is the persistent unit for configuration, run numbering, reports, and exported tests. The following tree is conceptual: language folders appear only when selected, and generated filenames vary with the flow.'),
code('<PROJECT_ROOT>/\n  .qa_studio_project.json\n  .env\n  .env.example\n  access-profiles.json\n  browser-settings.json\n  .browser_profiles/\n  Complete-Suite-Test-Report/\n    index.html\n    report-summary.json\n    Evidence/\n      Plans/  Screenshots/  Recording/  Trace/\n  docs/\n  Python_Playwright/\n  Java_Playwright/\n  TypeScript_Playwright/\n  JavaScript_Playwright/'),
table(['File or directory', 'Purpose'],[
['.qa_studio_project.json', 'Target settings, role accounts, sequence number, and run history. Contains reversible encoded secrets.'],
['.env and .env.example', 'Local runtime values versus example environment-variable keys. .env contains real secrets when configured.'],
['access-profiles.json', 'Role-to-environment-variable mappings for generated login code.'],
['browser-settings.json', 'Session policy, authentication markers, and configured timeout values.'],
['.browser_profiles', 'Saved browser state. The Studio and generated language projects keep separate profiles.'],
['Complete-Suite-Test-Report', 'Studio inspection/execution report with case evidence.'],
['Language folders', 'Framework configuration, page helpers, numbered tests, and execution reports from later runs.']],[.39,.61]),
p('Do not infer safety from a file extension or an ignore rule. A whole-project archive may include accounts and saved sessions. For a report-only handoff, use the report directory after reviewing its evidence.')
])

section('Running the exported projects', 'Developers and automation users', [
p('Select the desired languages under Advanced settings before generation. The desktop defaults to Python with scripts and a test plan enabled. The command line defaults to all four languages. Each generated project is a separate execution target.'),
table(['Folder', 'Framework', 'Run command'],[
['Python_Playwright', 'Python with pytest', 'python -m pytest'],
['Java_Playwright', 'Java with Maven and TestNG', 'mvn test'],
['TypeScript_Playwright', 'Playwright Test', 'npm test'],
['JavaScript_Playwright', 'Playwright Test', 'npm test']],[.38,.34,.28]),
h('Provision dependencies before the first run'),
code('# In Python_Playwright\npython -m pip install -r requirements.txt\npython -m pytest\n\n# In the selected JavaScript or TypeScript folder\nnpm install\nnpm test\n\n# In Java_Playwright with JDK 17 or newer and Maven\nmvn test'),
p('Set BASE_URL and the role credential values in the parent project .env. Review access-profiles.json for the expected variable names. The generated tests preserve their recorded login roles; changing a global selected role does not automatically rewrite explicit login steps.'),
h('Browser and report behavior'),
p('Set BROWSER_CHANNEL=chrome in the process environment when Chrome is required. JavaScript, TypeScript, and Java default to Edge. Fresh-mode Python attempts Edge, Chrome, and then available bundled Chromium; Python saved mode uses its configured channel, defaulting to Edge.'),
p('Each language writes a separate execution-reports/<RUN_ID>/ directory. Those results describe that later framework execution, not the earlier Studio run. Review the generated code before relying on it, install the language dependencies separately, and validate it against your own application.'),
p('For offline machines, prepare the dependency caches and toolchains in advance. The portable Studio does not bundle all language runtimes or every exported project dependency.')
])

section('Continuing and maintaining a workspace', 'Users and developers', [
h('Continue without losing the earlier run'),
steps('Back up the workspace when the previous results or custom code matter.', 'Use Open project rather than selecting a new empty output folder.', 'Confirm the target and role, enter the new flow, and run it.', 'Verify the new sequence appears in the generated files and report.', 'Keep a record of which source and configuration produced each result you use as evidence.'),
p('The workspace history advances sequential numbering. Earlier numbered flow scripts and report cases are kept. The report merges cases by identifier. Historical reports without current execution provenance are marked not_run when loaded into the current report schema.'),
h('Protect custom code'),
p('Regeneration writes shared configuration, page helpers, runtime helpers, and the master readme again. Do not assume that edits to generated support files will survive another Studio run. Keep custom changes under your own source control or in a separate maintained test project, and review differences before merging regenerated output.'),
p('The generic docs/Test_Plan_IEEE829.md copy is created only if it does not already exist. Prefer the numbered run plans and case evidence when you need the plan associated with a particular run, rather than assuming that generic copy is always the latest.'),
h('Keep execution contexts separate'),
p('The Studio saved profile and the profiles in generated language folders are separate local stores. A successful manual login in the Studio does not automatically authenticate every exported runner. Provision or validate each runner\'s own session as needed.'),
table(['Maintenance task', 'Recommended practice'],[
['Account changed or expired', 'Update the local profile and environment values; revalidate a short login flow.'],
['Application labels changed', 'Update the flow or maintained selectors, then regenerate and rerun.'],
['Storage growth', 'Archive approved evidence and remove only confirmed obsolete outputs while no run is active.'],
['Multiple concurrent jobs', 'Use isolated workspaces and saved profiles to avoid locks and cross-run state.']],[.35,.65])
])

section('Using the command line', 'Developers and automation users', [
p('The command line runs the same pipeline without the desktop interface. Use it for repeatable execution or a controlled build job. Supplying --cli requires --url; supplying --url also selects the command-line path.'),
h('Public application example'),
code('.\\.venv\\Scripts\\python main.py --cli `\n  --url "<TARGET_URL>" `\n  --flow \'click "<LINK>"; verify "<HEADING>"\' `\n  --langs Python `\n  --output "<OUTPUT_BASE>"'),
p('This is a PowerShell example. The backtick continues the command onto the next line. Replace placeholders before running it, and retain the outer single quotes around the flow so the internal double quotes are passed as part of the flow text.'),
h('Existing project with saved authentication'),
code('.\\.venv\\Scripts\\python main.py --cli `\n  --url "<TARGET_URL>" `\n  --flow \'Login as <ROLE>; verify "<SIGNED_IN_TEXT>"\' `\n  --profile "<ROLE>" `\n  --session-mode persistent `\n  --auth-success-path "<SIGNED_IN_PATH>" `\n  --auth-timeout 15 --auth-settle 2.5 `\n  --output "<EXISTING_PROJECT_ROOT>"'),
p('Configure the account in the workspace before this command. The CLI loads stored role accounts from the specified project root. It has no username or password command-line option; do not place passwords in the flow.'),
h('Check the exit code'),
p('Exit code 0 requires a passed flow and no accumulated pipeline errors. Exit code 1 indicates failure or the absence of a passing execution. In PowerShell, inspect $LASTEXITCODE immediately after the process completes. A generated report or a completed progress bar is not sufficient for a passing build.'),
p('Always supply an explicit --flow. The fallback exploration sentence is not an executable substitute for the supported grammar. There is no dedicated manual-capture CLI flag; use the desktop workflow for interactive capture.')
])

section('Command line and settings reference', 'Developers', [
table(['Option', 'Meaning and default'],[
['--cli', 'Select command-line mode. --url also selects this mode.'],
['--url', 'Target application address; required in command-line mode.'],
['--flow', 'Explicit ordered flow text. Supply this for a meaningful executable test.'],
['--output', 'Output base or existing project root. Default: ./output_workspace.'],
['--langs', 'One or more of Python Java TypeScript JavaScript. Default: all four. Use the displayed capitalization.'],
['--headed', 'Show the automated browser. Default CLI execution is headless.'],
['--profile', 'Saved role label from the existing project. Default: empty/public selection.'],
['--session-mode', 'fresh or persistent. Explicit value overrides loaded workspace settings.'],
['--auth-success-path', 'Authenticated route or full URL used as a success condition.'],
['--auth-success-selector', 'CSS selector expected to be visible after authentication.'],
['--auth-timeout', 'Login wait in seconds. Effective default: 15.'],
['--auth-settle', 'Continuous stable success window in seconds. Effective default: 2.5.']],[.37,.63]),
h('Stored browser configuration'),
code('{\n  "session_mode": "fresh",\n  "auth_success_path": "",\n  "auth_success_selector": "",\n  "auth_timeout_ms": 15000,\n  "auth_settle_ms": 2500\n}'),
p('CLI time values are converted from seconds to milliseconds in browser_settings. The authentication guard bounds the timeout between 3000 and 120000 milliseconds and the settle window between 500 milliseconds and timeout minus 500. The timeout applies to individual authentication waits, not to the entire pipeline.'),
p('The desktop writes its current settings into the workspace and browser-settings.json during generation. Generated runtimes read the latter. When using the CLI, browser settings begin with the stored workspace state and explicit CLI flags override them; editing only browser-settings.json is not a reliable way to override the Studio\'s loaded workspace settings.')
])

section('Troubleshooting access and login loops', 'All readers', [
p('A loop from login to dashboard and back to login means the session did not stay usable. The Studio is designed to stop and report this rather than endlessly retry credentials. Begin with a short login flow so the first failure is easy to inspect.'),
fig('authchoice', 'Figure 5  A practical decision path for a deployed login problem'),
table(['Symptom', 'Next check'],[
['Works in incognito only', 'Use Fresh (incognito-like). Compare behavior in a clean context and inspect the failing run.'],
['Brief dashboard then login', 'Set a real success marker. Review navigation routes and 401/403 responses; check the application session with its owner.'],
['No login form and saved session rejected', 'Provide an authenticated path or selector to verify reuse. Confirm it matches this environment.'],
['MFA or identity-provider challenge', 'Use manual sign-in with a saved profile, then run a separate automated validation.'],
['Login form appears late', 'Confirm the timeout is appropriate and inspect the delayed form. The guard waits for SPA entry state.'],
['Profile locked or browser will not launch', 'Close the managed browser and other jobs using that profile; check browser installation and policy logs.']],[.39,.61]),
p('A 401 or 403 is a diagnostic observation, not automatically a complete explanation. The target may have expired tokens, cookie scope problems, an identity-provider policy, or another server-side cause. Session isolation cannot fix those conditions. Provide sanitized reproduction steps and evidence to the application maintainer.'),
p('A short stable window does not guarantee that authentication lasts indefinitely. Later checks still watch for a visible password form, and application-specific final assertions are necessary.')
])

section('Troubleshooting flows and reports', 'All readers', [
table(['Problem', 'Likely check or corrective action'],[
['Unsupported instruction', 'Rewrite it using the action reference. Arbitrary prose, waits, and custom business assertions are not understood by the grammar.'],
['No unique visible target', 'Confirm the previous step succeeded, the target is visible, and the label or identifier is exact. Inspect the current page.'],
['Ambiguous target', 'Use a stable unique test ID or label. Ask the application team to distinguish repeated controls.'],
['Select fails on a dropdown', 'Check whether it is a native select. Use explicit clicks for a custom dropdown when its controls are supported.'],
['No matching API response', 'Move the assertion next to the triggering action and confirm the endpoint fragment. The action may not have sent XHR/fetch traffic.'],
['Unexpected API status', 'Inspect all matching responses. A mix including an unaccepted status causes the assertion to fail.'],
['Report exists but test failed', 'Read the executed status and first failure. Report creation is independent of a passing result.'],
['Only advisory plans shown as not run', 'Confirm whether manual mode was used and whether the primary flow has execution steps.'],
['Recording unavailable', 'Check recording runtime support and whether the browser context closed cleanly. Use actual screenshots and trace if present.'],
['Media links break after sharing', 'Copy the complete report directory and Evidence hierarchy, not just index.html.'],
['Generated suite cannot start', 'Install that language\'s dependencies, configure .env, and check the browser channel.'],
['Repeated creation now fails', 'Use appropriate fresh data or reset the fixture. The previous run may already have created the record.']],[.34,.66]),
h('Capture a useful issue description'),
p('Include the target environment category, session mode, flow with sensitive values replaced, first failed step, expected outcome, actual outcome, and relevant report evidence. Include the application build identifier if your team maintains one. Keep passwords, cookies, tokens, and personal records out of the shared description.'),
p('Change one input at a time when diagnosing. If the local demo passes but the deployed site fails, preserve that distinction; it narrows the investigation without proving which deployed component is responsible.')
])

section('System architecture', 'Developers and technical readers', [
p('The application is a local Python process with a desktop interface and a command-line entry point. LangGraph coordinates deterministic stages. Playwright controls a browser and observes the target application. Templates and runtime helpers produce the exported projects and local reports.'),
fig('architecture', 'Figure 6  Component boundaries and the two kinds of execution'),
h('Responsibilities at each boundary'),
p('The UI gathers inputs, starts background work, and displays progress and results. The CLI builds the same state and reports an exit code. The pipeline owns the ordered stages, while the browser layer owns context creation, authentication, live actions, telemetry, and evidence capture.'),
p('The planner prepares structured scenarios and plan text. The scaffolder writes language projects, configuration, and the report. Running those generated projects later creates a new execution in that framework, with its own evidence and report folder.'),
h('Local processing and network traffic'),
p('Parsing, planning, templating, and report assembly run locally without an external AI service. Browser navigation and application API calls still reach the target and any services it uses. Dependency installation is a separate provisioning activity that can require network access.'),
p('Core libraries are Playwright, LangGraph, Pydantic, Jinja2, and CustomTkinter. PyInstaller packages the Windows application. These are implementation dependencies, not a guarantee of application compatibility, cloud deployment support, or formal standards certification.')
])

section('Pipeline and execution lifecycle', 'Developers', [
fig('pipeline', 'Figure 7  Five deterministic stages and their outputs'),
table(['Stage', 'Main responsibility'],[
['Intent parser', 'Normalize the URL, resolve the role and output directory, and create ordered parsed steps.'],
['Browser inspector', 'Launch the selected context, execute or manually inspect, and produce an InspectionReport.'],
['Test planner', 'Build scenario definitions and optional plan text from the requested flow and inspection.'],
['Code synthesizer', 'Report selected language-generation stages; actual file rendering occurs in the scaffolder.'],
['Project scaffolder', 'Write projects and settings, generate the report, record run history, and save the workspace.']],[.3,.7]),
h('Failure does not erase the result'),
p('Browser inspection exceptions are converted into failed execution data, with later steps skipped. The pipeline can still generate a report showing that failure. errors accumulates failed-step messages; the CLI uses both execution_status and errors when deciding its exit code.'),
h('Manual mode follows a different inspection branch'),
p('Automatic mode calls the ordered executor. Manual mode opens the browser, waits for the capture signal, and inspects the current page state. Its execution step list is empty, so its execution status is not_run. The same downstream planning and scaffolding stages can still produce files.'),
h('UI concurrency'),
p('The desktop initiates the pipeline outside the UI event loop and relays progress back to the interface. Controls are disabled while a run is active to avoid overlapping actions in one window. A progress callback is part of AgentState; it reports processing activity rather than test success.'),
p('Keep the distinction between browser completion, report completion, and generated-suite execution in any extension. A new stage should not mark a plan or an unexecuted script as passed merely because its file was written.')
])

section('Flow parsing and locator resolution', 'Developers', [
h('Parsing preserves explicit intent'),
p('core/flow_parser.py protects quoted text before splitting instructions. It accepts semicolons, newlines, numbered lines, and selected conjunction boundaries. It inserts initial navigation and, when applicable, a role login. Every normalized step keeps its order, action type, target, input value, and accepted status codes. Unknown clauses become UNSUPPORTED steps.'),
h('Live resolution uses the current page'),
p('Before a supported control action, the executor reads the visible DOM again. It filters by compatible element type, then compares the requested target against visible labels and attributes such as ID, name, placeholder, data-testid, and aria-label. Exact matching is case-insensitive for these candidate names. Search also recognizes search-type inputs or search-related labels.'),
fig('locator', 'Figure 8  Strict control matching before an action is executed'),
p('One highest-scoring candidate is required. Multiple best candidates fail as ambiguous. No candidate after the bounded retry fails as missing. VERIFY_UI can also use a unique exact visible text match. These rules prevent a vague instruction from clicking an arbitrary first control.'),
h('Locator generation priority'),
p('The inspector prefers a unique data-testid, then ID, role and accessible name, placeholder, label, text, and finally CSS. It renders language-specific Playwright locator syntax. The action executor stores the locator chosen at the moment of execution so generated flows use the observed journey rather than an unrelated final-page control.'),
p('The current executor retries live target discovery for about four seconds and uses five-second timeouts for common control operations. Its default navigation timeout is 45 seconds. These are separate from authentication timeouts. Do not imply that raising the login timeout also changes every locator wait.'),
p('Iframe traversal, popup switching, and arbitrary shadow or custom-widget traversal are not promised by the flow grammar. Extend the execution and generation contracts explicitly when supporting a new action.')
])

section('Data models and state contracts', 'Developers', [
table(['Contract', 'Important fields and meaning'],[
['AgentState', 'Inputs such as target_url, user_flow_text, languages, profile, credentials, browser settings, and output directory; outputs such as steps, inspection report, scenarios, files, and errors.'],
['ParsedFlowStep', 'step_order, action_type, target_keyword, input_value, expected_status_codes. Defines the requested ordered action.'],
['DOMElement', 'Element identity, tag, role, label, attributes, locator strategy, and locator syntax by language.'],
['CapturedAPI', 'URL, method, resource type, status, request/response key lists, and triggering action. Status zero represents a network-level failure.'],
['InspectionReport', 'Elements, APIs, accessibility snapshot, login metadata, per-step results, execution status, duration, final URL, evidence paths, and authentication diagnostics.'],
['TestScenarioSpec and TestStepSpec', 'Structured planned cases and their action/locator definitions for planning and generation.']],[.33,.67]),
h('The execution record'),
code('{\n  "step_order": 2,\n  "action_type": "CLICK",\n  "target_keyword": "<CONTROL_LABEL>",\n  "status": "passed",\n  "duration_s": 0.42,\n  "error": "",\n  "locators": {"python": "<LOCATOR_CODE>"}\n}'),
p('This is a schematic record, not a captured result. Execution records also carry input and assertion fields, the current URL, and action-specific observations where applicable. Keep requested action data separate from the observed status.'),
h('Validation and serialization'),
p('Pydantic models describe the inspection structures and reject extra fields in the core inspection models. AgentState is a TypedDict used to pass pipeline data; it is not itself a secret store or an access-control boundary. Some state fields, such as callbacks and capture events, are live process objects rather than portable report data.'),
p('When adding a field, check its producer, consumers, serialized report representation, and all generated runtimes. A field appearing in a plan is not evidence that the browser captured or asserted it.')
])

section('Authentication and session internals', 'Developers', [
h('Profile identity'),
p('Saved profiles are created below .browser_profiles using a hash of the target origin, normalized role, and browser channel. The project root scopes the Studio store. Exported language folders have their own stores. This separates application sessions from the user\'s personal browser profile and avoids treating two roles as the same login.'),
h('Entry and stable success'),
p('The guard waits for a visible password field or a configured authenticated marker before deciding how to handle login. If a form exists, the login helper submits configured credentials. If no form exists, reuse requires an authenticated path or selector. Success requires no visible password field, the configured markers, and a visible nonempty body.'),
p('The success condition must remain true for the settle window, normally 2.5 seconds. The default authentication wait is 15 seconds, with bounded configurable values. A success path and selector are combined with AND when both are present. A brief route change by itself does not end the stability wait.'),
h('Loop detection and session loss'),
p('If a password form returns after apparent success during the login wait, the guard reports a login loop and stops without resubmitting credentials. Once authenticated, checks around flow actions report session loss when the password field becomes visible again. These checks are finite and primarily form-based; an application that loses authentication without showing that form still needs appropriate business or page assertions.'),
h('Diagnostics'),
p('The guard retains recent main-frame navigation routes and HTTP 401/403 responses, each capped at 30 entries. Its safe URL helper removes embedded user information, query parameters, and fragments while preserving scheme, host, port, and path. Other artifacts are not automatically covered by that sanitization.'),
h('Certificate behavior'),
p('The current Studio browser context and generated runtime contexts enable ignoring HTTPS certificate errors. This helps local fixtures but means these tests do not validate certificate trust. Successful HTTPS execution must not be represented as a certificate-security check.'),
p('Changing cookie policies, token expiry, identity-provider configuration, or corporate browser restrictions belongs to the target environment. The runner can expose a failure and isolate a context; it cannot guarantee compatibility with every sign-in design.')
])

section('Report generation and evidence integrity', 'Developers', [
fig('evidence', 'Figure 9  How an execution becomes a case and linked evidence'),
h('Status comes from execution'),
p('The primary case receives execution_status only when execution steps exist. Advisory scenarios receive not_run. Durations are derived from measured execution rather than invented defaults. A first failure leads to skipped dependent steps. The report must not claim a step ran solely because a planner produced its description.'),
h('Evidence comes from real files'),
p('The browser inspector captures viewport screenshots and available video and trace data into staging storage. The report generator copies existing artifacts into the report hierarchy and builds relative links. Missing recordings, traces, or screenshots are represented as unavailable rather than substituted with fabricated evidence.'),
p('The browser context closes to finalize recorded video. Media availability and test outcome are related operational facts but not identical: a passed assertion can have unavailable video, and a failed flow can still have useful real evidence.'),
h('Retention and compatibility'),
p('The report summary uses schema_version 2. Existing cases are merged by test identifier. Legacy cases without trustworthy execution provenance are changed to not_run, their old status is retained separately, and unsupported evidence references are removed. This avoids carrying older false passes into new totals.'),
p('Each exported framework writes to its own execution-reports/<RUN_ID> path. Keep the Studio report and later framework reports distinct in integrations. Their layouts and captured detail can differ; a common output format does not imply that every runtime collects exactly the same telemetry.'),
p('For automation integrations, read report-summary.json and the process exit code together. Validate statuses and required evidence according to the use case. An HTML file being present is only proof that report generation produced a file.')
])

section('Handling accounts evidence and operations', 'Users and developers', [
h('Know what needs protection'),
table(['Material', 'Handling requirement'],[
['.env', 'Contains plaintext account values. Keep local and exclude from shared reports or source archives.'],
['Workspace JSON', 'Contains reversible Base64 account data and project history. Treat it as sensitive.'],
['Saved browser profiles', 'May contain authenticated cookies and browser storage. Protect them like session credentials.'],
['Screenshots video and traces', 'May expose business records, page contents, tokens, or network details. Review before sharing.'],
['Flows and generated source', 'May contain test values, labels, endpoints, and internal application details. Review those values too.']],[.34,.66]),
h('Use suitable test environments'),
p('The runner performs the requested browser operations. It can create, update, or remove application data if your flow uses controls that do so. Use approved accounts and environments, define the required test data, and plan cleanup where a workflow changes records.'),
h('Prepare for restricted networks'),
p('Install and validate the browser and runtime dependencies before moving to an offline or restricted machine. The local engine does not require an AI service, but remote application access, identity-provider redirects, and initial package downloads still depend on the environment. A network restriction is not solved by switching the flow wording.'),
h('Maintain clear ownership of outputs'),
p('Agree where projects and evidence are stored, which copies are retained, and who can access them. Close active runs before archiving or removing folders. Back up important numbered tests and configuration before regeneration, because shared generated files can be rewritten.'),
h('What the current application does not provide'),
p('It is a local desktop and command-line tool, not a centralized multi-user test management service. It does not supply an encrypted credential vault, a built-in scheduler, organization-wide permissions, or automatic evidence retention rules. Teams that need those capabilities should integrate suitable external controls around the generated projects and output folders.')
])

section('Developing building and validating changes', 'Developers', [
h('Set up a development environment'),
code('python -m venv .venv\n.\\.venv\\Scripts\\python -m pip install -r requirements.txt\n.\\.venv\\Scripts\\python -m pip install -r requirements-dev.txt\n.\\.venv\\Scripts\\python main.py'),
p('Use the current requirements files as the dependency declarations. Prepare Node dependencies and Java/Maven tooling before cross-language checks. The regression fixtures use disposable local applications; exported sample failures can be intentional checks that failure reporting is correct.'),
table(['Regression area', 'Relevant module'],[
['Grammar execution and truthful reports', 'tests.test_flow_regressions'],
['Generated Python execution', 'tests.test_generated_execution'],
['Desktop and report layout/media', 'tests.test_desktop and tests.test_report_ui'],
['JavaScript TypeScript and Java', 'tests.test_other_languages and tests.test_java'],
['Deployed-style authentication fixtures', 'tests.test_deployed_auth'],
['Sessions across generated runtimes', 'tests.test_generated_sessions'],
['Packaged executable', 'tests.test_packaged']],[.45,.55]),
code('.\\.venv\\Scripts\\python -m unittest `\n  tests.test_flow_regressions tests.test_generated_execution `\n  tests.test_deployed_auth -v'),
h('Build a separate package'),
code('.\\.venv\\Scripts\\python -m PyInstaller `\n  PlaywrightEnterpriseQAStudio.spec --noconfirm `\n  --distpath "<DIST_DIRECTORY>" `\n  --workpath "<BUILD_WORK_DIRECTORY>"'),
p('Run packaged checks against the rebuilt executable and confirm that the full extracted folder works on the intended machine. Do not assume an older release folder was updated because a new build succeeded elsewhere.'),
p('The root test_phase scripts describe earlier behavior. Prefer the current tests package for regression coverage. Some cross-language tests expect prepared local runtime caches and generated fixture paths; inspect their setup before treating them as a portable CI recipe. Local fixtures verify specific mechanisms, not every deployed SSO configuration.')
])

section('Known limits and extension guidance', 'Users and developers', [
h('Current boundaries'),
bullets('The flow grammar supports explicit actions and simple visibility or HTTP-status checks. It is not an arbitrary natural-language reasoning engine.', 'Automated iframe traversal, popup switching, file uploads, and custom business assertions are not part of the current flow grammar.', 'Manual capture can inspect a manually reached state, but it does not reconstruct the entire journey or certify that the requested automated flow passed.', 'A passed API status assertion does not validate a response schema, all submitted values, or database persistence.', 'Authentication guards use finite waits and visible-page/form signals. They cannot guarantee session validity forever or support every SSO implementation.', 'Reports and generated code require review. Generated support files can be overwritten, and language runtimes may collect different levels of detail.'),
h('Extend an action end to end'),
steps('Define explicit grammar and normalized step fields for the new action.', 'Implement live execution with unique targeting, bounded waits, measured outcomes, and correct failure behavior.', 'Capture only evidence that was actually observed.', 'Implement matching generation behavior in every supported language, or fail explicitly where it is unsupported.', 'Add positive and negative regression fixtures, including missing/ambiguous targets and a failed dependent step.', 'Update user examples, limitations, and report interpretation.'),
h('Validate the target environment'),
p('Before adopting a new deployed application, run a small public navigation flow, a login flow with stable markers, a representative data-changing flow, and a deliberately failing assertion. Review both the Studio result and a selected exported runner. This checks whether success and failure are distinguishable in that environment.'),
p('Plan format names and historical schema labels are implementation conventions. They do not establish formal compliance or certification. Use the generated plan as a reviewable starting point and adapt it to your organization\'s actual test process.')
])

section('Glossary for shared understanding', 'All readers', [
table(['Term', 'Plain-language meaning'],[
['Assertion', 'A check that must be true for a step to pass.'],
['API', 'An application interface used by the browser to request or update data.'],
['Browser context', 'An isolated browser session with its own cookies and storage.'],
['DOM', 'The browser\'s structured representation of the page and its elements.'],
['Evidence', 'An actual captured artifact or observation supporting an execution result.'],
['Flow', 'The ordered actions and checks requested for one browser journey.'],
['Headless', 'Browser execution without a visible browser window.'],
['Locator', 'A rule Playwright uses to identify a page element.'],
['MFA', 'An additional sign-in challenge beyond a username and password.'],
['Origin', 'The scheme, host, and port of a web address; used to separate saved sessions.'],
['Profile', 'In account setup, a role and its credentials. In browser storage, a saved session directory. These are related but different.'],
['Scaffolding', 'Creating the initial files and folders of a reusable automation project.'],
['SPA', 'A web application that updates much of its interface dynamically without a full page reload.'],
['SSO', 'Sign-in coordinated through an identity provider rather than only a local login form.'],
['Trace', 'A recorded package of browser execution details for investigation.'],
['Workspace', 'The project folder holding settings, accounts, history, generated tests, and reports.']],[.24,.76]),
h('A useful reading habit'),
p('Ask three questions when reviewing any result: what was requested, what actually executed, and which evidence supports the conclusion. Keeping these separate helps both technical and nontechnical readers avoid treating a plan, a screenshot, or generated code as a broader guarantee than it provides.')
])

section('Source map and operational checklist', 'Users and developers', [
h('Implementation reference map'),
p('The following project-relative sources define the behavior explained in this guide. They are useful starting points for maintenance; they do not require a person-specific checkout path or repository account.'),
table(['Source', 'Read it for'],[
['main.py and gui/app_window.py', 'Entry points, command options, interface controls, and UI defaults.'],
['agents/workflow_graph.py and agents/state.py', 'Stage order and shared pipeline contracts.'],
['core/flow_parser.py and core/flow_executor.py', 'Supported grammar, live control matching, actions, assertions, and failure propagation.'],
['core/browser_inspector.py and core/browser_session.py', 'Browser lifecycle, media capture, login guards, and session diagnostics.'],
['core/workspace_manager.py', 'Accounts, stored settings, output naming, sequence history, and ignore rules.'],
['core/report_generator.py', 'Case statuses, pass-rate calculation, evidence links, and legacy migration.'],
['scaffolder/project_builder.py and flow_codegen.py', 'Generated directory structure and ordered flow code.'],
['scaffolder runtime helpers and template_registry.py', 'Per-language execution, authentication, configuration, and report behavior.'],
['tests package', 'Regression fixtures for execution, reports, packaging, and authentication.']],[.5,.5]),
h('Before a run'),
p('Confirm the target and environment, the role and login markers, supported ordered actions, expected assertions, suitable test data, and a writable project folder. Close another process that is using the same saved browser profile.'),
h('After a run'),
p('Read the first failed step if any, distinguish executed cases from plans, inspect the available evidence, and check the exit code when using the CLI. Preserve the full report hierarchy when sharing and exclude local credentials and session stores.'),
h('Before relying on exported automation'),
p('Review the generated flow, provision its toolchain, configure its own runtime environment and session, and execute it. Use that framework\'s fresh report as evidence of the exported suite\'s outcome.')
])
