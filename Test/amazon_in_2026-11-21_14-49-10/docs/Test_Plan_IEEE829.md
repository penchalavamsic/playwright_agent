---
test_id: "TP-IEEE829-001"
title: "To verify the functionality of "Online" → "Primary Navigation" → "Search" → "Input '12gb ram' and Submit""
module: "Online"
page: "Online Shopping site in India: Shop Online for Mobiles, Books, Watches, Shoes and More - Amazon.in"
section: "Primary Navigation"
control: "Search"
action: "Input '12gb ram' and Submit"
access_profile: "PUBLIC"
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

Verify the end-to-end functionality and backend API status code contracts for Online (Online Shopping site in India: Shop Online for Mobiles, Books, Watches, Shoes and More - Amazon.in) when executing the requested user flow.

# Preconditions

- `${BASE_URL}` is reachable.
- Credentials for `${TEST_ACCESS_PROFILE}` are configured.
- The required role and test data are available.
- The starting page is accessible without security blockades.

# Test Data

Use environment variables, runtime fixtures, or configuration keys:
- `${BASE_URL}`: Loaded from `.env`
- `${TEST_ACCESS_PROFILE}`: `PUBLIC` (resolved dynamically via `access-profiles.json` and `.env`)
- Target Locators: Prioritized Playwright locators (`data-testid` &rarr; `id` &rarr; `role+name`).

# Steps and Expected Results

1. Action: NAVIGATE on Browser Context with value 'https://www.amazon.in/' using locator `page.goto('https://www.amazon.in/')`.
   Expected Result: Navigate to application URL: https://www.amazon.in/. Successfully interact without DOM ambiguity. Expected status: [200].

2. Action: SEARCH on Search, alt, forward slash with value '12gb ram' using locator `page.locator("#nav-assist-search")`.
   Expected Result: Search value '12gb ram' into control 'Search, alt, forward slash'. Successfully interact without DOM ambiguity. Expected status: [200].

3. Action: CLICK on Add to Cart.
   Expected Result: Click interactive component 'Add to Cart'. Successfully interact without DOM ambiguity.

4. Action: CLICK on Cart, shift, alt, c using locator `page.locator("#nav-assist-cart")`.
   Expected Result: Click interactive component 'Cart, shift, alt, c'. Successfully interact without DOM ambiguity.

5. Action: VERIFY_UI on verify Checkout UI.
   Expected Result: Verify visibility and readiness of UI component 'verify Checkout UI'. Successfully interact without DOM ambiguity.

6. Action: VERIFY_API on Network Event Listener.
   Expected Result: Verify backend API response status ([200]) for endpoint '/1c5c1ecf7303/6ab7d267eef9/66125abca348/inputs'. Successfully interact without DOM ambiguity. Expected status: [200].

7. Action: NAVIGATE on Page with value 'https://www.amazon.in/' using locator `page.goto('https://www.amazon.in/')`.
   Expected Result: Open target URL: https://www.amazon.in/. Successfully interact without DOM ambiguity. Expected status: [200].

8. Action: VERIFY_UI on Document Title with value 'Online Shopping site in India: Shop Online for Mobiles, Books, Watches, Shoes and More - Amazon.in' using locator `expect(page).to_have_title(...)`.
   Expected Result: Verify Page Title equals or contains 'Online Shopping site in India: Shop Online for Mobiles, Books, Watches, Shoes and More - Amazon.in'. Successfully interact without DOM ambiguity.

9. Action: VERIFY_UI on main content using locator `page.locator("#nav-assist-skip-to-main-content")`.
   Expected Result: Verify visibility of core control 'main content' (a). Successfully interact without DOM ambiguity.

10. Action: VERIFY_UI on Search, alt, forward slash using locator `page.locator("#nav-assist-search")`.
   Expected Result: Verify visibility of core control 'Search, alt, forward slash' (a). Successfully interact without DOM ambiguity.

11. Action: VERIFY_UI on Cart, shift, alt, c using locator `page.locator("#nav-assist-cart")`.
   Expected Result: Verify visibility of core control 'Cart, shift, alt, c' (a). Successfully interact without DOM ambiguity.

12. Action: VERIFY_UI on Home, shift, alt, h using locator `page.locator("#nav-assist-home")`.
   Expected Result: Verify visibility of core control 'Home, shift, alt, h' (a). Successfully interact without DOM ambiguity.

# Network Verification

- Request URL: `https://1c5c1ecf7303.e10058c8.ap-south-1.token.awswaf.com/1c5c1ecf7303/6ab7d267eef9/66125abca348/inputs?client=browser`
- HTTP Method: `GET`
- Expected Status: `[200, 201]`
- Payload Presence: Yes (JSON keys: challenge, challenge_type, difficulty)
- Visible UI Result: Core interactive elements update state and remain responsive.

### Captured Network API & Status Code Verification Matrix

| Method | Endpoint Path | Observed Status | Target Assertion Status | Response Payload Keys | Triggered By Action |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `GET` | `/1c5c1ecf7303/6ab7d267eef9/66125abca348/inputs` | `200` | `200, 201` | `challenge, challenge_type, difficulty` | page_load |
| `POST` | `/1c5c1ecf7303/6ab7d267eef9/66125abca348/mp_verify` | `200` | `200, 201` | `token, inputs` | page_load |
| `GET` | `/images/G/01/csm/showads.v2.js` | `200` | `200, 201` | `[]` | page_load |
| `POST` | `/dram/renderLazyLoadedStreaming` | `200` | `200, 201` | `[]` | page_load |
| `GET` | `/hz/rhf` | `200` | `200, 201` | `html, success` | page_load |
| `POST` | `/1/events/com.amazon.csm.csa.prod` | `200` | `200, 201` | `[]` | page_load |
| `GET` | `/suggestions` | `200` | `200, 201` | `alias, predictiveText, prefix, responseId, shuffled` | probe:search -> typed '12gb ram' into searchbox 'Search Amazon.in' |
| `GET` | `/suggestions` | `200` | `200, 201` | `alias, predictiveText, prefix, responseId, shuffled` | probe:search -> typed '12gb ram' into searchbox 'Search Amazon.in' |
| `POST` | `/1/events/com.amazon.eel.SearchAutocompleteUIServiceMetrics.nexus` | `200` | `200, 201` | `[]` | probe:search -> typed '12gb ram' into searchbox 'Search Amazon.in' |
| `POST` | `/dram/renderLazyLoadedStreaming` | `200` | `200, 201` | `[]` | restore_navigation |
| `GET` | `/hz/rhf` | `200` | `200, 201` | `html, success` | restore_navigation |
| `POST` | `/1/events/com.amazon.csm.csa.prod` | `200` | `200, 201` | `[]` | probe:click link 'Cart, shift, alt, c' |
| `POST` | `/cart/enforcement/bannerAlert` | `200` | `200, 201` | `[]` | probe:click link '0 items in cart' |
| `GET` | `/ax/preauth` | `200` | `200, 201` | `icaEligible, token, data` | probe:click link '0 items in cart' |
| `GET` | `/hz/rhf` | `200` | `200, 201` | `html, success` | probe:click link '0 items in cart' |

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
| e1 | a (link) | main content | `page.locator("#nav-assist-skip-to-main-content")` | `page.locator("#nav-assist-skip-to-main-content")` | `page.locator('#nav-assist-skip-to-main-content')` |
| e2 | a (link) | Search, alt, forward slas | `page.locator("#nav-assist-search")` | `page.locator("#nav-assist-search")` | `page.locator('#nav-assist-search')` |
| e3 | a (link) | Cart, shift, alt, c | `page.locator("#nav-assist-cart")` | `page.locator("#nav-assist-cart")` | `page.locator('#nav-assist-cart')` |
| e4 | a (link) | Home, shift, alt, h | `page.locator("#nav-assist-home")` | `page.locator("#nav-assist-home")` | `page.locator('#nav-assist-home')` |
| e5 | a (link) | Your orders, shift, alt,  | `page.locator("#nav-assist-your-orders")` | `page.locator("#nav-assist-your-orders")` | `page.locator('#nav-assist-your-orders')` |
| e6 | button (button) | Show/hide shortcuts, shif | `page.locator("#nav-assist-show-shortcuts")` | `page.locator("#nav-assist-show-shortcuts")` | `page.locator('#nav-assist-show-shortcuts')` |
| e7 | a (link) | Amazon.in | `page.locator("#nav-logo-sprites")` | `page.locator("#nav-logo-sprites")` | `page.locator('#nav-logo-sprites')` |
| e8 | a (button) | Delivering to Bengaluru 5 | `page.locator("#nav-global-location-popover-link")` | `page.locator("#nav-global-location-popover-link")` | `page.locator('#nav-global-location-popover-link')` |
| e9 | select (combobox) | Select the department you | `page.locator("#searchDropdownBox")` | `page.locator("#searchDropdownBox")` | `page.locator('#searchDropdownBox')` |
| e10 | input (searchbox) | Search Amazon.in | `page.locator("#twotabsearchtextbox")` | `page.locator("#twotabsearchtextbox")` | `page.locator('#twotabsearchtextbox')` |
| e11 | input (button) | Go | `page.locator("#nav-search-submit-button")` | `page.locator("#nav-search-submit-button")` | `page.locator('#nav-search-submit-button')` |
| e12 | a (link) | Choose a language for sho | `page.get_by_role("link", name="Choose a language for shopping in Amazon India. The current selection is English (EN).", exact=True)` | `page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Choose a language for shopping in Amazon India. The current selection is English (EN).").setExact(true))` | `page.getByRole('link', { name: 'Choose a language for shopping in Amazon India. The current selection is English (EN).', exact: true })` |
| e13 | button (button) | Expand to Change Language | `page.locator("#icp-nav-flyout > button")` | `page.locator("#icp-nav-flyout > button")` | `page.locator('#icp-nav-flyout > button')` |
| e14 | a (link) | Hello, sign in Account &  | `page.get_by_role("link", name="Hello, sign in Account & Lists", exact=True)` | `page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Hello, sign in Account & Lists").setExact(true))` | `page.getByRole('link', { name: 'Hello, sign in Account & Lists', exact: true })` |
| e15 | button (button) | Expand Account and Lists | `page.get_by_role("button", name="Expand Account and Lists", exact=True)` | `page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Expand Account and Lists").setExact(true))` | `page.getByRole('button', { name: 'Expand Account and Lists', exact: true })` |
| e16 | a (link) | Returns & Orders | `page.locator("#nav-orders")` | `page.locator("#nav-orders")` | `page.locator('#nav-orders')` |
| e17 | a (link) | 0 items in cart | `page.locator("#nav-cart")` | `page.locator("#nav-cart")` | `page.locator('#nav-cart')` |
| e18 | a (button) | Open All Categories Menu | `page.locator("#nav-hamburger-menu")` | `page.locator("#nav-hamburger-menu")` | `page.locator('#nav-hamburger-menu')` |
| e19 | a (link) | Amazon Pay | `page.get_by_role("link", name="Amazon Pay", exact=True)` | `page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Amazon Pay").setExact(true))` | `page.getByRole('link', { name: 'Amazon Pay', exact: true })` |
| e20 | a (link) | Mobiles | `page.get_by_role("link", name="Mobiles", exact=True)` | `page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Mobiles").setExact(true))` | `page.getByRole('link', { name: 'Mobiles', exact: true })` |
| e21 | a (link) | Flights | `page.get_by_role("link", name="Flights", exact=True)` | `page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Flights").setExact(true))` | `page.getByRole('link', { name: 'Flights', exact: true })` |
| e22 | a (link) | Today's Deals | `page.get_by_role("link", name="Today's Deals", exact=True)` | `page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Today's Deals").setExact(true))` | `page.getByRole('link', { name: 'Today\'s Deals', exact: true })` |
| e23 | a (link) | Coupons | `page.get_by_role("link", name="Coupons", exact=True)` | `page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Coupons").setExact(true))` | `page.getByRole('link', { name: 'Coupons', exact: true })` |
| e24 | a (link) | New Releases | `page.get_by_role("link", name="New Releases", exact=True)` | `page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("New Releases").setExact(true))` | `page.getByRole('link', { name: 'New Releases', exact: true })` |
| e25 | a (link) | Electronics | `page.locator("a[href=\"/electronics/b/?ie=UTF8&node=976419031&ref_=nav_cs_electronics\"]")` | `page.locator("a[href=\"/electronics/b/?ie=UTF8&node=976419031&ref_=nav_cs_electronics\"]")` | `page.locator('a[href="/electronics/b/?ie=UTF8&node=976419031&ref_=nav_cs_electronics"]')` |