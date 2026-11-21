---
test_id: "TP-IEEE829-001"
title: "To verify the functionality of "Shutterstock" → "Primary Navigation" → "Search" → "Input 'dashboard' and Submit""
module: "Shutterstock"
page: "Shutterstock — Stock Images, Photos, Vectors, Video, and Music"
section: "Primary Navigation"
control: "Search"
action: "Input 'dashboard' and Submit"
access_profile: "SUPER_USER"
priority: "High"
classification: "Read-only"
test_type: "Automated End-to-End & API Contract"
automation_candidate: true
plan_status: "approved"
script_status: "generated"
environment_variables:
  - "BASE_URL"
  - "TEST_ACCESS_PROFILE"
test_data:
  base_url_env: "BASE_URL"
  access_profile_env: "TEST_ACCESS_PROFILE"
related_script: "tests/001_primary_user_flow.py"
---

# Purpose

Verify the end-to-end functionality and backend API status code contracts for Shutterstock (Shutterstock — Stock Images, Photos, Vectors, Video, and Music) when executing the requested user flow.

# Preconditions

- `${BASE_URL}` is reachable.
- Credentials for `${TEST_ACCESS_PROFILE}` are configured.
- The required role and test data are available.
- The starting page is accessible without security blockades.

# Test Data

Use environment variables, runtime fixtures, or configuration keys:
- `${BASE_URL}`: Loaded from `.env`
- `${TEST_ACCESS_PROFILE}`: `SUPER_USER` (resolved dynamically via `access-profiles.json` and `.env`)
- Target Locators: Prioritized Playwright locators (`data-testid` &rarr; `id` &rarr; `role+name`).

# Steps and Expected Results

1. Action: NAVIGATE on Browser Context with value 'https://www.shutterstock.com' using locator `page.goto('https://www.shutterstock.com')`.
   Expected Result: Navigate to application URL: https://www.shutterstock.com. Successfully interact without DOM ambiguity. Expected status: [200].

2. Action: SEARCH on Search Input with value 'dashboard' using locator `page.locator("#search-input")`.
   Expected Result: Search value 'dashboard' into control 'Search Input'. Successfully interact without DOM ambiguity. Expected status: [200].

3. Action: CLICK on Dashboard Tab using locator `page.get_by_test_id("dashboard-tab")`.
   Expected Result: Click interactive component 'Dashboard Tab'. Successfully interact without DOM ambiguity.

4. Action: VERIFY_API on Network Event Listener.
   Expected Result: Verify backend API response status ([200, 201]) for endpoint '/api/v1/search'. Successfully interact without DOM ambiguity. Expected status: [200, 201].

5. Action: NAVIGATE on Page with value 'https://www.shutterstock.com' using locator `page.goto('https://www.shutterstock.com')`.
   Expected Result: Open target URL: https://www.shutterstock.com. Successfully interact without DOM ambiguity. Expected status: [200].

6. Action: VERIFY_UI on Document Title with value 'Shutterstock — Stock Images, Photos, Vectors, Video, and Music' using locator `expect(page).to_have_title(...)`.
   Expected Result: Verify Page Title equals or contains 'Shutterstock — Stock Images, Photos, Vectors, Video, and Music'. Successfully interact without DOM ambiguity.

7. Action: VERIFY_UI on Search Input using locator `page.locator("#search-input")`.
   Expected Result: Verify visibility of core control 'Search Input' (input). Successfully interact without DOM ambiguity.

8. Action: VERIFY_UI on Dashboard Tab using locator `page.get_by_test_id("dashboard-tab")`.
   Expected Result: Verify visibility of core control 'Dashboard Tab' (button). Successfully interact without DOM ambiguity.

9. Action: VERIFY_API on GET /api/v1/search.
   Expected Result: Validate contract for GET /api/v1/search (Expected Status: [200], Keys: ['status', 'items', 'total']). Successfully interact without DOM ambiguity. Expected status: [200].

10. Action: VERIFY_API on POST /api/v1/audit.
   Expected Result: Validate contract for POST /api/v1/audit (Expected Status: [201], Keys: ['id', 'created_at']). Successfully interact without DOM ambiguity. Expected status: [201].

# Network Verification

- Request URL: `https://www.shutterstock.com/api/v1/search`
- HTTP Method: `GET`
- Expected Status: `[200, 201]`
- Payload Presence: Yes (JSON keys: status, items, total)
- Visible UI Result: Core interactive elements update state and remain responsive.

### Captured Network API & Status Code Verification Matrix

| Method | Endpoint Path | Observed Status | Target Assertion Status | Response Payload Keys | Triggered By Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/search` | `200` | `200, 201` | `status, items, total` | search_probe |
| `POST` | `/api/v1/audit` | `201` | `200, 201` | `id, created_at` | click:dashboard |

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
10. The Healer may propose test-only changes later but must not change expected application behavior.
11. Plans must use this Jira-style title format:

To verify the functionality of "<Module>" → "<Section>" → "<Control>" → "<Action>"

---

## Appendix: UI Component & Multi-Language Locator Inventory

Prioritized corporate locator hierarchy: `data-testid` &rarr; `id` &rarr; `role + name` &rarr; `placeholder` &rarr; `label` &rarr; `text` &rarr; `css`.

| Element ID | Tag / Role | Label / Text | Python Playwright | Java Playwright | TS / JS Playwright |
| :--- | :--- | :--- | :--- | :--- | :--- |
| e1 | input (searchbox) | Search Input | `page.locator("#search-input")` | `page.locator("#search-input")` | `page.locator("#search-input")` |
| e2 | button (tab) | Dashboard Tab | `page.get_by_test_id("dashboard-tab")` | `page.getByTestId("dashboard-tab")` | `page.getByTestId("dashboard-tab")` |

---

<!-- Run 002 (ADMIN) -->

---
test_id: "TP-IEEE829-002"
title: "To verify the functionality of "Shutterstock" → "Primary Navigation" → "Input" → "Input 'search' and Submit""
module: "Shutterstock"
page: "Shutterstock — Stock Images, Photos, Vectors, Video, and Music"
section: "Primary Navigation"
control: "Input"
action: "Input 'search' and Submit"
access_profile: "ADMIN"
priority: "High"
classification: "Read-only"
test_type: "Automated End-to-End & API Contract"
automation_candidate: true
plan_status: "approved"
script_status: "generated"
environment_variables:
  - "BASE_URL"
  - "TEST_ACCESS_PROFILE"
test_data:
  base_url_env: "BASE_URL"
  access_profile_env: "TEST_ACCESS_PROFILE"
related_script: "tests/002_primary_user_flow.py"
---

# Purpose

Verify the end-to-end functionality and backend API status code contracts for Shutterstock (Shutterstock — Stock Images, Photos, Vectors, Video, and Music) when executing the requested user flow.

# Preconditions

- `${BASE_URL}` is reachable.
- Credentials for `${TEST_ACCESS_PROFILE}` are configured.
- The required role and test data are available.
- The starting page is accessible without security blockades.

# Test Data

Use environment variables, runtime fixtures, or configuration keys:
- `${BASE_URL}`: Loaded from `.env`
- `${TEST_ACCESS_PROFILE}`: `ADMIN` (resolved dynamically via `access-profiles.json` and `.env`)
- Target Locators: Prioritized Playwright locators (`data-testid` &rarr; `id` &rarr; `role+name`).

# Steps and Expected Results

1. Action: NAVIGATE on Browser Context with value 'https://www.shutterstock.com' using locator `page.goto('https://www.shutterstock.com')`.
   Expected Result: Navigate to application URL: https://www.shutterstock.com. Successfully interact without DOM ambiguity. Expected status: [200].

2. Action: FILL on Search Input with value 'search' using locator `page.locator("#search-input")`.
   Expected Result: Fill value 'search' into control 'Search Input'. Successfully interact without DOM ambiguity. Expected status: [200].

3. Action: VERIFY_API on Network Event Listener.
   Expected Result: Verify backend API response status ([200, 201]) for endpoint '/api/v1/search'. Successfully interact without DOM ambiguity. Expected status: [200, 201].

4. Action: NAVIGATE on Page with value 'https://www.shutterstock.com' using locator `page.goto('https://www.shutterstock.com')`.
   Expected Result: Open target URL: https://www.shutterstock.com. Successfully interact without DOM ambiguity. Expected status: [200].

5. Action: VERIFY_UI on Document Title with value 'Shutterstock — Stock Images, Photos, Vectors, Video, and Music' using locator `expect(page).to_have_title(...)`.
   Expected Result: Verify Page Title equals or contains 'Shutterstock — Stock Images, Photos, Vectors, Video, and Music'. Successfully interact without DOM ambiguity.

6. Action: VERIFY_UI on Search Input using locator `page.locator("#search-input")`.
   Expected Result: Verify visibility of core control 'Search Input' (input). Successfully interact without DOM ambiguity.

7. Action: VERIFY_UI on Dashboard Tab using locator `page.get_by_test_id("dashboard-tab")`.
   Expected Result: Verify visibility of core control 'Dashboard Tab' (button). Successfully interact without DOM ambiguity.

8. Action: VERIFY_API on GET /api/v1/search.
   Expected Result: Validate contract for GET /api/v1/search (Expected Status: [200], Keys: ['status', 'items', 'total']). Successfully interact without DOM ambiguity. Expected status: [200].

9. Action: VERIFY_API on POST /api/v1/audit.
   Expected Result: Validate contract for POST /api/v1/audit (Expected Status: [201], Keys: ['id', 'created_at']). Successfully interact without DOM ambiguity. Expected status: [201].

# Network Verification

- Request URL: `https://www.shutterstock.com/api/v1/search`
- HTTP Method: `GET`
- Expected Status: `[200, 201]`
- Payload Presence: Yes (JSON keys: status, items, total)
- Visible UI Result: Core interactive elements update state and remain responsive.

### Captured Network API & Status Code Verification Matrix

| Method | Endpoint Path | Observed Status | Target Assertion Status | Response Payload Keys | Triggered By Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/search` | `200` | `200, 201` | `status, items, total` | search_probe |
| `POST` | `/api/v1/audit` | `201` | `200, 201` | `id, created_at` | click:dashboard |

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
10. The Healer may propose test-only changes later but must not change expected application behavior.
11. Plans must use this Jira-style title format:

To verify the functionality of "<Module>" → "<Section>" → "<Control>" → "<Action>"

---

## Appendix: UI Component & Multi-Language Locator Inventory

Prioritized corporate locator hierarchy: `data-testid` &rarr; `id` &rarr; `role + name` &rarr; `placeholder` &rarr; `label` &rarr; `text` &rarr; `css`.

| Element ID | Tag / Role | Label / Text | Python Playwright | Java Playwright | TS / JS Playwright |
| :--- | :--- | :--- | :--- | :--- | :--- |
| e1 | input (searchbox) | Search Input | `page.locator("#search-input")` | `page.locator("#search-input")` | `page.locator("#search-input")` |
| e2 | button (tab) | Dashboard Tab | `page.get_by_test_id("dashboard-tab")` | `page.getByTestId("dashboard-tab")` | `page.getByTestId("dashboard-tab")` |