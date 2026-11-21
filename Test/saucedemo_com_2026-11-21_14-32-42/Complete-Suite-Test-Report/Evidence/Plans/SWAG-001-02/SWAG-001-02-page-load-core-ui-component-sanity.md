---
test_id: "SWAG-001-02"
title: "To verify the functionality of \"Swag\" → \"Swag Labs\" → \"Page Load & Core UI Component Sanity\""
module: "Swag"
page: "Swag Labs"
section: "Primary Flow"
control: "Interactive Controls"
action: "Execution & Verification"
access_profile: "STANDARD_USER"
priority: "High"
classification: "Read-only"
test_type: "Positive"
automation_candidate: true
plan_status: "reviewed"
script_status: "generated"
environment_variables:
  - BASE_URL
  - TEST_ACCESS_PROFILE
test_data: {}
related_script: "tests/page-load-core-ui-component-sanity.spec.ts"
---

# Purpose

Verify the functionality of "Swag" → "Swag Labs" → "Page Load & Core UI Component Sanity" under access profile `STANDARD_USER`.

# Preconditions

- `${BASE_URL}` is reachable.
- Credentials for `${TEST_ACCESS_PROFILE}` (`STANDARD_USER`) are configured in `.env`.

# Test Data

Use environment variables and runtime fixtures.

# Steps and Expected Results

1. Action: Open target URL: https://www.saucedemo.com.
   Expected Result: Step completes deterministically without UI or network errors.

2. Action: Verify Page Title equals or contains 'Swag Labs'.
   Expected Result: Step completes deterministically without UI or network errors.

3. Action: Verify visibility of core control 'Open Menu' (button).
   Expected Result: Step completes deterministically without UI or network errors.

4. Action: Verify visibility of core control 'All Items' (a).
   Expected Result: Step completes deterministically without UI or network errors.

5. Action: Verify visibility of core control 'Dynamic Catalog' (a).
   Expected Result: Step completes deterministically without UI or network errors.

6. Action: Verify visibility of core control 'About' (a).
   Expected Result: Step completes deterministically without UI or network errors.

7. Action: Verify visibility of core control 'Logout' (a).
   Expected Result: Step completes deterministically without UI or network errors.

# Network Verification

- Request URL: `${BASE_URL}/api/summed-events/submit`
- HTTP Method: POST
- Expected Status: 401
- Payload Presence: Verified response payload
- Visible UI Result: Interactive controls visible and responsive

# Expected Final Result

All steps and network status assertions succeed for SWAG-001-02.

# Classification

- Read-only
- Positive

# Restrictions

- Do not include credentials, tokens, cookies, authorization codes, or sensitive payloads.
- Do not use static environment-specific data.

# Generation Status

- Test script generation: Complete
- CI/CD execution: Ready
- Healing: Ready
