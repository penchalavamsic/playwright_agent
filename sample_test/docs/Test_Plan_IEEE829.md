---
test_id: "TP-IEEE829-1794294117"
title: "To verify the functionality of "YouTube" → "Primary Navigation" → "Search" → "Input 'Veera' and Submit""
module: "YouTube"
page: "YouTube"
section: "Primary Navigation"
control: "Search"
action: "Input 'Veera' and Submit"
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
  target_url: "https://www.youtube.com/"
  flow_prompt: "go to that URL and search for Veera Veera Song in search bar,"
related_script: "tests/test_automation_suite.py"
---

# Purpose

Verify the end-to-end functionality and backend API status code contracts for YouTube (YouTube) when executing the user flow: "go to that URL and search for Veera Veera Song in search bar,".

# Preconditions

- `${LIMAS_BASE_URL}` is reachable (configured for target: `https://www.youtube.com/`).
- Credentials for `${TEST_ACCESS_PROFILE}` are configured.
- The required role and test data are available.
- The starting page is accessible without security blockades.

# Test Data

Use environment variables, runtime fixtures, or configuration keys:
- `${LIMAS_BASE_URL}`: `https://www.youtube.com/`
- Access Profile: `ADMIN`
- Target Locators: Prioritized Playwright locators (`data-testid` &rarr; `id` &rarr; `role+name`).

# Steps and Expected Results

1. Action: NAVIGATE on Browser Context with value 'https://www.youtube.com/' using locator `page.goto('https://www.youtube.com/')`.
   Expected Result: Navigate to application URL: https://www.youtube.com/. Successfully interact without DOM ambiguity. Expected status: [200].

2. Action: SEARCH on Search with value 'Veera' using locator `page.get_by_role("combobox", name="Search", exact=True)`.
   Expected Result: Search value 'Veera' into control 'Search'. Successfully interact without DOM ambiguity. Expected status: [200].

3. Action: NAVIGATE on Page with value 'https://www.youtube.com/' using locator `page.goto('https://www.youtube.com/')`.
   Expected Result: Open target URL: https://www.youtube.com/. Successfully interact without DOM ambiguity. Expected status: [200].

4. Action: VERIFY_UI on Document Title with value 'YouTube' using locator `expect(page).to_have_title(...)`.
   Expected Result: Verify Page Title equals or contains 'YouTube'. Successfully interact without DOM ambiguity.

5. Action: VERIFY_UI on Guide using locator `page.get_by_role("button", name="Guide", exact=True)`.
   Expected Result: Verify visibility of core control 'Guide' (button). Successfully interact without DOM ambiguity.

6. Action: VERIFY_UI on YouTube Home using locator `page.get_by_role("link", name="YouTube Home", exact=True)`.
   Expected Result: Verify visibility of core control 'YouTube Home' (a). Successfully interact without DOM ambiguity.

7. Action: VERIFY_UI on Skip navigation using locator `page.get_by_role("button", name="Skip navigation", exact=True)`.
   Expected Result: Verify visibility of core control 'Skip navigation' (button). Successfully interact without DOM ambiguity.

8. Action: VERIFY_UI on Search using locator `page.get_by_role("combobox", name="Search", exact=True)`.
   Expected Result: Verify visibility of core control 'Search' (input). Successfully interact without DOM ambiguity.

9. Action: VERIFY_UI on Search using locator `page.get_by_role("button", name="Search", exact=True)`.
   Expected Result: Verify visibility of core control 'Search' (button). Successfully interact without DOM ambiguity.

10. Action: VERIFY_API on GET /pagead/id.
   Expected Result: Validate contract for GET /pagead/id (Expected Status: [200], Keys: []). Successfully interact without DOM ambiguity. Expected status: [200].

11. Action: VERIFY_API on POST /youtubei/v1/guide.
   Expected Result: Validate contract for POST /youtubei/v1/guide (Expected Status: [200], Keys: ['responseContext', 'items', 'trackingParams']). Successfully interact without DOM ambiguity. Expected status: [200].

12. Action: VERIFY_API on POST /youtubei/v1/feedback.
   Expected Result: Validate contract for POST /youtubei/v1/feedback (Expected Status: [200], Keys: ['responseContext', 'feedbackResponses']). Successfully interact without DOM ambiguity. Expected status: [200].

# Network Verification

- Request URL: `https://googleads.g.doubleclick.net/pagead/id?slf_rd=1`
- HTTP Method: `GET`
- Expected Status: `[200, 201]`
- Payload Presence: No / Standard response payload
- Visible UI Result: Core interactive elements update state and remain responsive.

### Captured Network API & Status Code Verification Matrix

| Method | Endpoint Path | Observed Status | Target Assertion Status | Response Payload Keys | Triggered By Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/pagead/id` | `302` | `302` | `[]` | page_load |
| `GET` | `/pagead/id` | `200` | `200, 201` | `[]` | page_load |
| `POST` | `/youtubei/v1/guide` | `200` | `200, 201` | `responseContext, items, trackingParams` | page_load |
| `POST` | `/youtubei/v1/feedback` | `200` | `200, 201` | `responseContext, feedbackResponses` | page_load |
| `GET` | `/` | `301` | `301` | `[]` | page_load |
| `GET` | `/` | `0` | `0` | `[]` | page_load |
| `GET` | `/videoplayback` | `403` | `403` | `[]` | page_load |
| `GET` | `/videoplayback` | `403` | `403` | `[]` | page_load |
| `GET` | `/s/i/youtube_outline_experimental/search/v16/24px.svg` | `200` | `200, 201` | `[]` | page_load |
| `GET` | `/videoplayback` | `0` | `0` | `[]` | page_load |
| `GET` | `/videoplayback` | `0` | `0` | `[]` | page_load |
| `GET` | `/s/i/youtube_outline_experimental/menu/v1/24px.svg` | `200` | `200, 201` | `[]` | page_load |
| `GET` | `/s/i/youtube_outline_experimental/chevron_down/v10/24px.svg` | `200` | `200, 201` | `[]` | page_load |
| `GET` | `/s/i/youtube_outline_experimental/overflow_vertical/v14/24px.svg` | `200` | `200, 201` | `[]` | page_load |
| `GET` | `/s/i/youtube_outline_experimental/person_circle/v10/24px.svg` | `200` | `200, 201` | `[]` | page_load |

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
| e1 | button (button) | Guide | `page.get_by_role("button", name="Guide", exact=True)` | `page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Guide").setExact(true))` | `page.getByRole('button', { name: 'Guide', exact: true })` |
| e2 | a (link) | YouTube Home | `page.get_by_role("link", name="YouTube Home", exact=True)` | `page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("YouTube Home").setExact(true))` | `page.getByRole('link', { name: 'YouTube Home', exact: true })` |
| e3 | button (button) | Skip navigation | `page.get_by_role("button", name="Skip navigation", exact=True)` | `page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Skip navigation").setExact(true))` | `page.getByRole('button', { name: 'Skip navigation', exact: true })` |
| e4 | input (combobox) | Search | `page.get_by_role("combobox", name="Search", exact=True)` | `page.getByRole(AriaRole.COMBOBOX, new Page.GetByRoleOptions().setName("Search").setExact(true))` | `page.getByRole('combobox', { name: 'Search', exact: true })` |
| e5 | button (button) | Search | `page.get_by_role("button", name="Search", exact=True)` | `page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Search").setExact(true))` | `page.getByRole('button', { name: 'Search', exact: true })` |
| e6 | button (button) | Search with your voice | `page.get_by_role("button", name="Search with your voice", exact=True)` | `page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Search with your voice").setExact(true))` | `page.getByRole('button', { name: 'Search with your voice', exact: true })` |
| e7 | a |  | `page.locator("ytd-topbar-menu-button-renderer > div > a")` | `page.locator("ytd-topbar-menu-button-renderer > div > a")` | `page.locator('ytd-topbar-menu-button-renderer > div > a')` |
| e8 | button (button) | Settings | `page.get_by_role("button", name="Settings", exact=True)` | `page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Settings").setExact(true))` | `page.getByRole('button', { name: 'Settings', exact: true })` |
| e9 | a (link) | Sign in | `page.locator("a[href=\"https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en&ec=65620\"]")` | `page.locator("a[href=\"https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en&ec=65620\"]")` | `page.locator('a[href="https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en&ec=65620"]')` |
| e10 | a (link) | Home | `page.locator("a[title=\"Home\"]")` | `page.locator("a[title=\"Home\"]")` | `page.locator('a[title="Home"]')` |
| e11 | a (link) | Shorts | `page.locator("a[title=\"Shorts\"]")` | `page.locator("a[title=\"Shorts\"]")` | `page.locator('a[title="Shorts"]')` |
| e12 | a (link) | Subscriptions | `page.locator("a[title=\"Subscriptions\"]")` | `page.locator("a[title=\"Subscriptions\"]")` | `page.locator('a[title="Subscriptions"]')` |
| e13 | a (link) | You | `page.locator("a[title=\"You\"]")` | `page.locator("a[title=\"You\"]")` | `page.locator('a[title="You"]')` |
| e14 | a (link) | History | `page.locator("a[title=\"History\"]")` | `page.locator("a[title=\"History\"]")` | `page.locator('a[title="History"]')` |
| e15 | a (link) | Sign in | `page.locator("a[href=\"https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en\"]")` | `page.locator("a[href=\"https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en\"]")` | `page.locator('a[href="https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en"]')` |
| e16 | a (link) | Music | `page.locator("a[title=\"Music\"]")` | `page.locator("a[title=\"Music\"]")` | `page.locator('a[title="Music"]')` |
| e17 | a (link) | Movies & TV | `page.locator("a[title=\"Movies & TV\"]")` | `page.locator("a[title=\"Movies & TV\"]")` | `page.locator('a[title="Movies & TV"]')` |
| e18 | a (link) | Live | `page.locator("a[title=\"Live\"]")` | `page.locator("a[title=\"Live\"]")` | `page.locator('a[title="Live"]')` |
| e19 | ytd-guide-entry-renderer (button) | Show more | `page.locator("#expander-item")` | `page.locator("#expander-item")` | `page.locator('#expander-item')` |
| e20 | a (link) | Show more | `page.locator("a[title=\"Show more\"]")` | `page.locator("a[title=\"Show more\"]")` | `page.locator('a[title="Show more"]')` |
| e21 | a (link) | Try Premium for $0 | `page.locator("a[title=\"Try Premium for $0\"]")` | `page.locator("a[title=\"Try Premium for $0\"]")` | `page.locator('a[title="Try Premium for $0"]')` |
| e22 | a (link) | YouTube Music | `page.locator("a[title=\"YouTube Music\"]")` | `page.locator("a[title=\"YouTube Music\"]")` | `page.locator('a[title="YouTube Music"]')` |
| e23 | a (link) | YouTube Kids | `page.locator("a[title=\"YouTube Kids\"]")` | `page.locator("a[title=\"YouTube Kids\"]")` | `page.locator('a[title="YouTube Kids"]')` |
| e24 | a (link) | YouTube Labs | `page.locator("a[title=\"YouTube Labs\"]")` | `page.locator("a[title=\"YouTube Labs\"]")` | `page.locator('a[title="YouTube Labs"]')` |
| e25 | a (link) | Report history | `page.locator("a[title=\"Report history\"]")` | `page.locator("a[title=\"Report history\"]")` | `page.locator('a[title="Report history"]')` |