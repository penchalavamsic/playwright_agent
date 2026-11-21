---
test_id: "AMAZON-001-01"
title: "To verify the functionality of \"Amazon\" → \"Online Shopping site in India: Shop Online for Mobiles, Books, Watches, Shoes and More - Amazon.in\" → \"Primary User Flow & API Status Verification\""
module: "Amazon"
page: "Online Shopping site in India: Shop Online for Mobiles, Books, Watches, Shoes and More - Amazon.in"
section: "Primary Flow"
control: "Interactive Controls"
action: "Execution & Verification"
access_profile: "PUBLIC"
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
related_script: "tests/primary-user-flow-api-status-verification.spec.ts"
---

# Purpose

Verify the functionality of "Amazon" → "Online Shopping site in India: Shop Online for Mobiles, Books, Watches, Shoes and More - Amazon.in" → "Primary User Flow & API Status Verification" under access profile `PUBLIC`.

# Preconditions

- `${BASE_URL}` is reachable.
- Credentials for `${TEST_ACCESS_PROFILE}` (`PUBLIC`) are configured in `.env`.

# Test Data

Use environment variables and runtime fixtures.

# Steps and Expected Results

1. Action: Navigate to application URL: https://www.amazon.in/.
   Expected Result: Step completes deterministically without UI or network errors.

2. Action: Search value '12gb ram' into control 'Search, alt, forward slash'.
   Expected Result: Step completes deterministically without UI or network errors.

3. Action: Click interactive component 'Add to Cart'.
   Expected Result: Step completes deterministically without UI or network errors.

4. Action: Click interactive component 'Cart, shift, alt, c'.
   Expected Result: Step completes deterministically without UI or network errors.

5. Action: Verify visibility and readiness of UI component 'verify Checkout UI'.
   Expected Result: Step completes deterministically without UI or network errors.

6. Action: Verify backend API response status ([200]) for endpoint '/1c5c1ecf7303/6ab7d267eef9/66125abca348/inputs'.
   Expected Result: Step completes deterministically without UI or network errors.

# Network Verification

- Request URL: `${BASE_URL}/1c5c1ecf7303/6ab7d267eef9/66125abca348/inputs`
- HTTP Method: GET
- Expected Status: 200
- Payload Presence: Verified response payload
- Visible UI Result: Interactive controls visible and responsive

# Expected Final Result

All steps and network status assertions succeed for AMAZON-001-01.

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
