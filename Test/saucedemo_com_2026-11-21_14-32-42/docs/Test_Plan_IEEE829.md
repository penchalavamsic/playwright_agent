---
test_id: "TP-IEEE829-001"
title: "To verify the functionality of "Swag" → "Primary Navigation" → "Input" → "Input 'search' and Submit""
module: "Swag"
page: "Swag Labs"
section: "Primary Navigation"
control: "Input"
action: "Input 'search' and Submit"
access_profile: "STANDARD_USER"
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

Verify the end-to-end functionality and backend API status code contracts for Swag (Swag Labs) when executing the requested user flow.

# Preconditions

- `${BASE_URL}` is reachable.
- Credentials for `${TEST_ACCESS_PROFILE}` are configured.
- The required role and test data are available.
- The starting page is accessible without security blockades.

# Test Data

Use environment variables, runtime fixtures, or configuration keys:
- `${BASE_URL}`: Loaded from `.env`
- `${TEST_ACCESS_PROFILE}`: `STANDARD_USER` (resolved dynamically via `access-profiles.json` and `.env`)
- Target Locators: Prioritized Playwright locators (`data-testid` &rarr; `id` &rarr; `role+name`).

# Steps and Expected Results

1. Action: NAVIGATE on Browser Context with value 'https://www.saucedemo.com' using locator `page.goto('https://www.saucedemo.com')`.
   Expected Result: Navigate to application URL: https://www.saucedemo.com. Successfully interact without DOM ambiguity. Expected status: [200].

2. Action: FILL on input with value 'search'.
   Expected Result: Fill value 'search' into control 'input'. Successfully interact without DOM ambiguity. Expected status: [200].

3. Action: CLICK on LinkedIn using locator `page.get_by_role("link", name="LinkedIn", exact=True)`.
   Expected Result: Click interactive component 'LinkedIn'. Successfully interact without DOM ambiguity.

4. Action: VERIFY_API on Network Event Listener.
   Expected Result: Verify backend API response status ([200]) for endpoint '/api/summed-events/submit'. Successfully interact without DOM ambiguity. Expected status: [200].

5. Action: NAVIGATE on Page with value 'https://www.saucedemo.com' using locator `page.goto('https://www.saucedemo.com')`.
   Expected Result: Open target URL: https://www.saucedemo.com. Successfully interact without DOM ambiguity. Expected status: [200].

6. Action: VERIFY_UI on Document Title with value 'Swag Labs' using locator `expect(page).to_have_title(...)`.
   Expected Result: Verify Page Title equals or contains 'Swag Labs'. Successfully interact without DOM ambiguity.

7. Action: VERIFY_UI on Open Menu using locator `page.get_by_role("button", name="Open Menu", exact=True)`.
   Expected Result: Verify visibility of core control 'Open Menu' (button). Successfully interact without DOM ambiguity.

8. Action: VERIFY_UI on All Items using locator `page.locator("#inventory_sidebar_link")`.
   Expected Result: Verify visibility of core control 'All Items' (a). Successfully interact without DOM ambiguity.

9. Action: VERIFY_UI on Dynamic Catalog using locator `page.locator("#dynamic_catalog_sidebar_link")`.
   Expected Result: Verify visibility of core control 'Dynamic Catalog' (a). Successfully interact without DOM ambiguity.

10. Action: VERIFY_UI on About using locator `page.locator("#about_sidebar_link")`.
   Expected Result: Verify visibility of core control 'About' (a). Successfully interact without DOM ambiguity.

11. Action: VERIFY_UI on Logout using locator `page.locator("#logout_sidebar_link")`.
   Expected Result: Verify visibility of core control 'Logout' (a). Successfully interact without DOM ambiguity.

12. Action: VERIFY_API on POST /api/summed-events/submit.
   Expected Result: Validate contract for POST /api/summed-events/submit (Expected Status: [401], Keys: ['error']). Successfully interact without DOM ambiguity. Expected status: [401].

# Network Verification

- Request URL: `https://events.backtrace.io/api/summed-events/submit?universe=UNIVERSE&token=TOKEN`
- HTTP Method: `POST`
- Expected Status: `[401]`
- Payload Presence: Yes (JSON keys: error)
- Visible UI Result: Core interactive elements update state and remain responsive.

### Captured Network API & Status Code Verification Matrix

| Method | Endpoint Path | Observed Status | Target Assertion Status | Response Payload Keys | Triggered By Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/summed-events/submit` | `401` | `401` | `error` | page_load |
| `POST` | `/api/unique-events/submit` | `401` | `401` | `error` | page_load |

# Expected Final Result

One clear and independently verifiable result: The automation flow completes deterministically with 100% UI locator fidelity and all backend API calls return expected status codes (401).

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
| e1 | button (button) | Open Menu | `page.get_by_role("button", name="Open Menu", exact=True)` | `page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Open Menu").setExact(true))` | `page.getByRole('button', { name: 'Open Menu', exact: true })` |
| e2 | a (button) | All Items | `page.locator("#inventory_sidebar_link")` | `page.locator("#inventory_sidebar_link")` | `page.locator('#inventory_sidebar_link')` |
| e3 | a (button) | Dynamic Catalog | `page.locator("#dynamic_catalog_sidebar_link")` | `page.locator("#dynamic_catalog_sidebar_link")` | `page.locator('#dynamic_catalog_sidebar_link')` |
| e4 | a (link) | About | `page.locator("#about_sidebar_link")` | `page.locator("#about_sidebar_link")` | `page.locator('#about_sidebar_link')` |
| e5 | a (button) | Logout | `page.locator("#logout_sidebar_link")` | `page.locator("#logout_sidebar_link")` | `page.locator('#logout_sidebar_link')` |
| e6 | a (button) | Reset App State | `page.locator("#reset_sidebar_link")` | `page.locator("#reset_sidebar_link")` | `page.locator('#reset_sidebar_link')` |
| e7 | button (button) | Close Menu | `page.get_by_text("Close Menu", exact=True)` | `page.getByText("Close Menu", new Page.GetByTextOptions().setExact(true))` | `page.getByText('Close Menu', { exact: true })` |
| e8 | a (button) | Cart, empty | `page.get_by_role("button", name="Cart, empty", exact=True)` | `page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Cart, empty").setExact(true))` | `page.getByRole('button', { name: 'Cart, empty', exact: true })` |
| e9 | select (combobox) | Sort products | `page.get_by_role("combobox", name="Sort products", exact=True)` | `page.getByRole(AriaRole.COMBOBOX, new Page.GetByRoleOptions().setName("Sort products").setExact(true))` | `page.getByRole('combobox', { name: 'Sort products', exact: true })` |
| e10 | a (button) | View details for Sauce La | `page.locator("#item_4_img_link")` | `page.locator("#item_4_img_link")` | `page.locator('#item_4_img_link')` |
| e11 | a (button) | View details for Sauce La | `page.locator("#item_4_title_link")` | `page.locator("#item_4_title_link")` | `page.locator('#item_4_title_link')` |
| e12 | button (button) | Add to cart | `page.locator("#add-to-cart-sauce-labs-backpack")` | `page.locator("#add-to-cart-sauce-labs-backpack")` | `page.locator('#add-to-cart-sauce-labs-backpack')` |
| e13 | a (button) | View details for Sauce La | `page.locator("#item_0_img_link")` | `page.locator("#item_0_img_link")` | `page.locator('#item_0_img_link')` |
| e14 | a (button) | View details for Sauce La | `page.locator("#item_0_title_link")` | `page.locator("#item_0_title_link")` | `page.locator('#item_0_title_link')` |
| e15 | button (button) | Add to cart | `page.locator("#add-to-cart-sauce-labs-bike-light")` | `page.locator("#add-to-cart-sauce-labs-bike-light")` | `page.locator('#add-to-cart-sauce-labs-bike-light')` |
| e16 | a (button) | View details for Sauce La | `page.locator("#item_1_img_link")` | `page.locator("#item_1_img_link")` | `page.locator('#item_1_img_link')` |
| e17 | a (button) | View details for Sauce La | `page.locator("#item_1_title_link")` | `page.locator("#item_1_title_link")` | `page.locator('#item_1_title_link')` |
| e18 | button (button) | Add to cart | `page.locator("#add-to-cart-sauce-labs-bolt-t-shirt")` | `page.locator("#add-to-cart-sauce-labs-bolt-t-shirt")` | `page.locator('#add-to-cart-sauce-labs-bolt-t-shirt')` |
| e19 | a (button) | View details for Sauce La | `page.locator("#item_5_img_link")` | `page.locator("#item_5_img_link")` | `page.locator('#item_5_img_link')` |
| e20 | a (button) | View details for Sauce La | `page.locator("#item_5_title_link")` | `page.locator("#item_5_title_link")` | `page.locator('#item_5_title_link')` |
| e21 | button (button) | Add to cart | `page.locator("#add-to-cart-sauce-labs-fleece-jacket")` | `page.locator("#add-to-cart-sauce-labs-fleece-jacket")` | `page.locator('#add-to-cart-sauce-labs-fleece-jacket')` |
| e22 | a (button) | View details for Sauce La | `page.locator("#item_2_img_link")` | `page.locator("#item_2_img_link")` | `page.locator('#item_2_img_link')` |
| e23 | a (button) | View details for Sauce La | `page.locator("#item_2_title_link")` | `page.locator("#item_2_title_link")` | `page.locator('#item_2_title_link')` |
| e24 | button (button) | Add to cart | `page.locator("#add-to-cart-sauce-labs-onesie")` | `page.locator("#add-to-cart-sauce-labs-onesie")` | `page.locator('#add-to-cart-sauce-labs-onesie')` |
| e25 | a (button) | View details for Test.all | `page.locator("#item_3_img_link")` | `page.locator("#item_3_img_link")` | `page.locator('#item_3_img_link')` |