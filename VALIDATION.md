# Flow execution and report repair

Review date: 22 November 2026. Project: `E:\MySpace\Projects\playwright_agent`.

## Deployed authentication and simpler UI

The desktop now keeps the URL, login profile, flow and Run button on the main screen. Account editing is collapsible. Session settings, script languages and output location are under Advanced settings; logs and technical counters are in Details. Results display individual step outcomes and failure reasons without a duplicate completion dialog. The default and expanded layouts were inspected at the minimum 1100 × 720 window size.

Fresh browser contexts remain the default. Dedicated saved profiles are separated by origin, role and browser. Authentication waits for delayed forms and a stable success marker, verifies existing sessions before reuse, detects a return to login, and stops dependent actions without retrying credentials. Reports include sanitized navigation paths and 401/403 responses. The same policy is included in generated Python, JavaScript, TypeScript and Java suites.

Cross-language verification caught and corrected two Java-specific problems: a relative browser-profile path could stall Edge startup, and resolving an empty URI discarded the starting URL's final path segment. Generated Java now uses an absolute profile path with a startup timeout and preserves the exact initial target URL. All guards tolerate transient execution-context replacement during redirects while continuing their bounded authentication checks.

The new fixture in `tests/test_deployed_auth.py` reproduces login → dashboard → login with a 401 response, cookie expiry during a flow, delayed SPA forms, persistent-cookie reuse, and HTTPS Secure-cookie redirects. Its self-signed certificate and private key are exclusively local test fixtures. HTTPS tests use the application's existing `ignore_https_errors` setting, so they verify secure-cookie/session behavior rather than certificate trust validation.

No deployed office URL has been supplied. These checks establish local HTTP/HTTPS behavior and explicit failure reporting; they do not establish that the user's specific deployment, SSO provider, or corporate policies work.

## Findings and changes

| Problem found | Corrected behavior |
| --- | --- |
| Browser inspection ran a few probes, restored the initial page, and did not execute the requested sequence. | An ordered executor resolves controls on the current page after each action. It supports login, fill, click, search, native select, checkbox, keypress, navigation and visibility/API assertions. |
| Keyword splitting discarded or misclassified instructions and lost quoted values. | An explicit grammar preserves quoted punctuation and conjunctions. Unknown instructions fail explicitly. |
| Generated primary tests searched for the literal word `playwright`, ignoring the user's flow. | All four languages emit the actual ordered steps, supplied values, and execution-time locators. Unresolved actions fail explicitly in generated tests. |
| Reports marked every generated scenario passed and invented durations. | Only executed steps determine results and measured durations. Advisory scenarios remain `not_run`. |
| Missing screenshots, video and trace files were replaced with placeholder files. | Only real captured files are linked. Missing media is stated as unavailable. |
| Report screenshots were reused and relabeled as unrelated steps. | Screenshots retain their original capture order and labels. |
| Auto-login was considered successful immediately after submission. | Login requires the password control to disappear; failed authentication stops the flow. Explicit post-login assertions remain useful for application-specific authentication checks. |
| An unrelated successful API request could stand in for the requested check. | Live assertions correlate responses to the preceding action and requested endpoint/status. |
| Python generated `page.page.locator(...)`, and pytest used an invalid browser name. | Login locator prefixes and pytest configuration are corrected. |
| Framework runs overwrote the Studio report and each other's evidence. | Each framework writes a separate timestamped execution report. |
| Python setup failures were absent from report totals. | Setup, call and teardown outcomes are collected. Missing video is not linked. |
| Java TestNG was wired to the old aggregate test, and media lifecycle was not used by the numbered test. | TestNG registers numbered tests and uses the shared screenshot/video/trace lifecycle. |
| Duplicate control labels could produce duplicate POM method names. | Generated POM member names are unique. |
| Reopening reports could preserve old fabricated pass results. | Legacy summaries without execution provenance are marked `not_run`, with their prior status retained as legacy metadata. |
| The desktop demo pointed to an old localhost port. | Load Demo Portal starts an actual local server, supplies demo credentials, and loads an executable flow. |
| The GUI showed successful completion regardless of test outcome. | Generation completion and flow outcome are displayed separately; failed flow details remain available. |
| Subsequent GUI runs could go back to the parent output folder. | The completed project becomes the selected output path for the next run. |
| The Windows build searched only a redirected LOCALAPPDATA cache and omitted FFmpeg. | Packaging also checks the real user cache and the existing release's media runtime, including available FFmpeg revisions. |

## Verification

Outcome: **27 distinct regression checks passed** across the verification groups below. The original repair had 18 checks; this update adds seven authentication checks, an integration check exercising all four generated session runners, and a packaged saved-session/loop check. Python source compilation and `git diff --check` also completed successfully.

The test application is the disposable portal in `core/demo_portal.py`. Its task creation endpoint rejects incorrect title, priority or checkbox values, so simply clicking through the UI does not satisfy the passing test.

The current checks cover:

- Parser order, quoted punctuation, numbered steps, role normalization and unsupported instructions.
- Real login, task-page navigation, form input, native select, checkbox selection, POST 201 and visible confirmation.
- Wrong credentials, a missing control, failed HTTP 503 and skipped dependent steps.
- Browser launch failure reporting and legacy report migration.
- Python, JavaScript, TypeScript and Java generated test execution with both a passing journey and an intentionally unresolved journey.
- Python fixture/setup errors appearing as failures in the execution report.
- Multiple runs appended to one project and preservation of the original inspection report during generated-test runs.
- Desktop demo generation, output path retention and failure status display.
- Offline report filtering/search, evidence links, real Playwright trace contents, and desktop/mobile layout.
- Packaged executable execution from a different working directory, generating all four languages, reporting success/failure exit codes, and capturing real screenshot/video/trace files.
- Browser playback of the packaged application's WebM, with nonzero video dimensions and advancing playback time.

Current verification logs: `tmp/session-ui-tests.log` (10 checks covering initial session support and all generated languages), `tmp/deployed-release-tests.log` (16 checks covering flows, desktop, packaged sessions and report UI), `tmp/simple-ui-final.log` (final desktop check), `tmp/sessions-verified-final.log` (all eight authentication/generated-session checks after the Java and redirect-race fixes), and `tmp/package-verified-final.log` (final executable and recorded-video checks). These groups overlap. Logs include intentional generated-test failures; the enclosing regression test requires those failures and must finish with `OK`.

The final sample project is recorded in `tmp/latest_packaged.txt`. Earlier cross-language sample projects are recorded in `tmp/latest_verification.txt`. They are local test artifacts under `verification_output/`, excluded from Git.

## Scope and remaining limits

TaskLink was inspected read-only as a possible fixture. Its SQL file contains schema definitions but no seeded user accounts. The reproducible portal was used instead, and no TaskLink files were changed.

These checks run on this Windows machine against localhost. Corporate browser restrictions, network/proxy settings, SSO/MFA and the user's office deployment were not available for direct verification. Browser failures now produce an explicit failed result rather than a successful-looking report.

The offline parser is intentionally bounded. It does not understand arbitrary natural-language business workflows. Automated iframe traversal, popup switching and file upload are not implemented. Interactive capture records a manual session without claiming that the described flow was executed. The two additional advisory plans are not runnable coverage guarantees.

Historical output reports and the older `dist_release` package have not been replaced. Use the new `dist_verified` package. A legacy project's report is migrated when that project is next regenerated.

The current portable archive is `dist_verified/PlaywrightEnterpriseQAStudio-deployed-ready.zip`. The earlier `PlaywrightEnterpriseQAStudio-verified.zip` remains the previous build. Extract the current archive completely and keep `_internal` beside the executable.
