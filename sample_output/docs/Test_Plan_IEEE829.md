---
test_id: "TP-IEEE829-1794298070"
title: "To verify the functionality of "Acme" → "Primary Navigation" → "Search" → "Input 'search' and Submit""
module: "Acme"
page: "Acme QA Portal"
section: "Primary Navigation"
control: "Search"
action: "Input 'search' and Submit"
access_profile: "ADMIN"
priority: "High"
classification: "Read-only"
test_type: "Automated End-to-End & API Contract"
automation_candidate: true
plan_status: "approved"
script_status: "generated"
environment_variables:
  - "LIMAS_BASE_URL"
  - "TEST_ACCESS_PROFILE"
test_data:
  target_url: "http://127.0.0.1:59141/"
  flow_prompt: "Create automation script for the dashboard, search API, click button and verify whether it succeeded with 200 or 201 status code"
related_script: "tests/test_automation_suite.py"
---

# Purpose

Verify the end-to-end functionality and backend API status code contracts for Acme (Acme QA Portal) when executing the user flow: "Create automation script for the dashboard, search API, click button and verify whether it succeeded with 200 or 201 status code".

# Preconditions

- `${LIMAS_BASE_URL}` is reachable (configured for target: `http://127.0.0.1:59141/`).
- Credentials for `${TEST_ACCESS_PROFILE}` are configured.
- The required role and test data are available.
- The starting page is accessible without security blockades.

# Test Data

Use environment variables, runtime fixtures, or configuration keys:
- `${LIMAS_BASE_URL}`: `http://127.0.0.1:59141/`
- Access Profile: `ADMIN`
- Target Locators: Prioritized Playwright locators (`data-testid` &rarr; `id` &rarr; `role+name`).

# Steps and Expected Results

1. Action: NAVIGATE on Browser Context with value 'http://127.0.0.1:59141/' using locator `page.goto('http://127.0.0.1:59141/')`.
   Expected Result: Navigate to application URL: http://127.0.0.1:59141/. Successfully interact without DOM ambiguity. Expected status: [200].

2. Action: VERIFY_UI on Dashboard using locator `page.get_by_role("tab", name="Dashboard", exact=True)`.
   Expected Result: Verify visibility and readiness of UI component 'Dashboard'. Successfully interact without DOM ambiguity.

3. Action: SEARCH on Search with value 'search' using locator `page.locator("#global-search")`.
   Expected Result: Search value 'search' into control 'Search'. Successfully interact without DOM ambiguity. Expected status: [200].

4. Action: VERIFY_API on Network Event Listener.
   Expected Result: Verify backend API response status ([200, 201]) for endpoint '/api/user'. Successfully interact without DOM ambiguity. Expected status: [200, 201].

5. Action: CLICK on Go using locator `page.get_by_test_id("search-submit")`.
   Expected Result: Click interactive component 'Go'. Successfully interact without DOM ambiguity.

6. Action: VERIFY_API on Network Event Listener.
   Expected Result: Verify backend API response status ([200, 201]) for endpoint '/api/user'. Successfully interact without DOM ambiguity. Expected status: [200, 201].

7. Action: NAVIGATE on Page with value 'http://127.0.0.1:59141/' using locator `page.goto('http://127.0.0.1:59141/')`.
   Expected Result: Open target URL: http://127.0.0.1:59141/. Successfully interact without DOM ambiguity. Expected status: [200].

8. Action: VERIFY_UI on Document Title with value 'Acme QA Portal' using locator `expect(page).to_have_title(...)`.
   Expected Result: Verify Page Title equals or contains 'Acme QA Portal'. Successfully interact without DOM ambiguity.

9. Action: VERIFY_UI on Home using locator `page.get_by_role("link", name="Home", exact=True)`.
   Expected Result: Verify visibility of core control 'Home' (a). Successfully interact without DOM ambiguity.

10. Action: VERIFY_UI on Docs using locator `page.get_by_role("link", name="Docs", exact=True)`.
   Expected Result: Verify visibility of core control 'Docs' (a). Successfully interact without DOM ambiguity.

11. Action: VERIFY_UI on External using locator `page.get_by_role("link", name="External", exact=True)`.
   Expected Result: Verify visibility of core control 'External' (a). Successfully interact without DOM ambiguity.

12. Action: VERIFY_UI on Search using locator `page.locator("#global-search")`.
   Expected Result: Verify visibility of core control 'Search' (input). Successfully interact without DOM ambiguity.

# Network Verification

- Request URL: `http://127.0.0.1:59141/api/user`
- HTTP Method: `GET`
- Expected Status: `[200, 201]`
- Payload Presence: Yes (JSON keys: id, name, roles, email)
- Visible UI Result: Core interactive elements update state and remain responsive.

### Captured Network API & Status Code Verification Matrix

| Method | Endpoint Path | Observed Status | Target Assertion Status | Response Payload Keys | Triggered By Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/validate` | `400` | `400` | `error, fields` | page_load |
| `GET` | `/api/user` | `200` | `200, 201` | `id, name, roles, email` | page_load |
| `GET` | `/api/feature-flags` | `401` | `401` | `error, code` | page_load |
| `GET` | `/api/legacy-endpoint` | `404` | `404` | `error, path` | page_load |
| `GET` | `/api/admin/settings` | `403` | `403` | `error, requiredRole` | page_load |
| `GET` | `/api/config` | `200` | `200, 201` | `key, value` | page_load |
| `PUT` | `/api/preferences` | `204` | `204` | `[]` | page_load |
| `GET` | `/api/search` | `200` | `200, 201` | `query, results, total` | probe:search -> typed 'test' into searchbox 'Search' |
| `GET` | `/api/search` | `200` | `200, 201` | `query, results, total` | probe:search -> typed 'test' into searchbox 'Search' |
| `GET` | `/api/dashboard` | `200` | `200, 201` | `widgets, updatedAt, owner` | probe:click tab 'Dashboard' |
| `POST` | `/api/events` | `201` | `200, 201` | `eventId, status` | probe:click tab 'Dashboard' |

# Expected Final Result

One clear and independently verifiable result: The automation flow completes deterministically with 100% UI locator fidelity and all backend API calls return expected status codes (200, 201).

# Classification

- Read-only or Data-changing: Read-only (Non-destructive safe probes only)
- Category: Positive, API, Functional E2E

# Restrictions

- Do not include credentials, tokens, cookies, authorization codes, or sensitive payloads.
- Do not repeat data-changing submissions.
- Do not manually navigate to simulate a successful result.
- Do not use static environment-specific data.

# Generation Status

- Test script generation: Complete (Python, Java, TypeScript, JavaScript)
- CI/CD execution: Ready
- Healing: Ready

# Dynamic Plan Rules

1. Use only behavior verified through Playwright MCP.
2. Verify one atomic behavior per plan.
3. Do not hardcode application URLs.
4. Do not hardcode usernames or passwords.
5. Do not hardcode user names, emails, request IDs, license IDs, hardware IDs, dates, User Groups, Profiles, Roles, feature names, versions, or local paths.
6. Use environment variables, access-profiles.json, runtime fixtures, or test-data configuration.
7. Select exactly one access profile:
   - SUPER_USER
   - ADMIN
   - SUPER_USER_ADMIN_USER
8. Keep every plan shareable between environments and team members.
9. CI/CD owns test execution.
10. The Healer may propose test-only changes later but must not change expected LIMAS behavior.
11. Plans must use this Jira-style title format:

To verify the functionality of "<Module>" → "<Section>" → "<Control>" → "<Action>"

---

## Appendix: UI Component & Multi-Language Locator Inventory

Prioritized corporate locator hierarchy: `data-testid` &rarr; `id` &rarr; `role + name` &rarr; `placeholder` &rarr; `label` &rarr; `text` &rarr; `css`.

| Element ID | Tag / Role | Label / Text | Python Playwright | Java Playwright | TS / JS Playwright |
| :--- | :--- | :--- | :--- | :--- | :--- |
| e1 | a (link) | Home | `page.get_by_role("link", name="Home", exact=True)` | `page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Home").setExact(true))` | `page.getByRole('link', { name: 'Home', exact: true })` |
| e2 | a (link) | Docs | `page.get_by_role("link", name="Docs", exact=True)` | `page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Docs").setExact(true))` | `page.getByRole('link', { name: 'Docs', exact: true })` |
| e3 | a (link) | External | `page.get_by_role("link", name="External", exact=True)` | `page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("External").setExact(true))` | `page.getByRole('link', { name: 'External', exact: true })` |
| e4 | input (searchbox) | Search | `page.locator("#global-search")` | `page.locator("#global-search")` | `page.locator('#global-search')` |
| e5 | button (button) | Go | `page.get_by_test_id("search-submit")` | `page.getByTestId("search-submit")` | `page.getByTestId('search-submit')` |
| e6 | button (tab) | Overview | `page.get_by_role("tab", name="Overview", exact=True)` | `page.getByRole(AriaRole.TAB, new Page.GetByRoleOptions().setName("Overview").setExact(true))` | `page.getByRole('tab', { name: 'Overview', exact: true })` |
| e7 | button (tab) | Dashboard | `page.get_by_role("tab", name="Dashboard", exact=True)` | `page.getByRole(AriaRole.TAB, new Page.GetByRoleOptions().setName("Dashboard").setExact(true))` | `page.getByRole('tab', { name: 'Dashboard', exact: true })` |
| e8 | button (tab) | Reports | `page.get_by_role("tab", name="Reports", exact=True)` | `page.getByRole(AriaRole.TAB, new Page.GetByRoleOptions().setName("Reports").setExact(true))` | `page.getByRole('tab', { name: 'Reports', exact: true })` |
| e9 | input (textbox) | Email | `page.get_by_role("textbox", name="Email", exact=True)` | `page.getByRole(AriaRole.TEXTBOX, new Page.GetByRoleOptions().setName("Email").setExact(true))` | `page.getByRole('textbox', { name: 'Email', exact: true })` |
| e10 | input (textbox) | Coupon code | `page.get_by_role("textbox", name="Coupon code", exact=True)` | `page.getByRole(AriaRole.TEXTBOX, new Page.GetByRoleOptions().setName("Coupon code").setExact(true))` | `page.getByRole('textbox', { name: 'Coupon code', exact: true })` |
| e11 | select (combobox) |  | `page.locator("select[name=\"country\"]")` | `page.locator("select[name=\"country\"]")` | `page.locator('select[name="country"]')` |
| e12 | textarea (textbox) |  | `page.locator("textarea[name=\"notes\"]")` | `page.locator("textarea[name=\"notes\"]")` | `page.locator('textarea[name="notes"]')` |
| e13 | button (button) | Save profile | `page.get_by_role("button", name="Save profile", exact=True)` | `page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Save profile").setExact(true))` | `page.getByRole('button', { name: 'Save profile', exact: true })` |
| e14 | a (link) | Learn more | `page.locator("a[href=\"#a\"]")` | `page.locator("a[href=\"#a\"]")` | `page.locator('a[href="#a"]')` |
| e15 | a (link) | Learn more | `page.locator("a[href=\"#b\"]")` | `page.locator("a[href=\"#b\"]")` | `page.locator('a[href="#b"]')` |
| e16 | div (button) | Help | `page.get_by_test_id("help-widget")` | `page.getByTestId("help-widget")` | `page.getByTestId('help-widget')` |
| e17 | button (button) | Delete Account | `page.get_by_test_id("delete-account")` | `page.getByTestId("delete-account")` | `page.getByTestId('delete-account')` |