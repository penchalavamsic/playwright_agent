---
test_id: "LIMAS-AUTH-011"
title: "To verify the functionality of \"Authentication\" → \"Sign In button\" → \"Navigate to Keycloak\""
module: "Authentication"
page: "Login page"
section: "Sign In button"
control: "Sign In button"
action: "Navigation to Keycloak"
access_profile: "SUPER_USER_ADMIN_USER"
priority: "Critical"
classification: "Read-only"
test_type: "Positive"
automation_candidate: true
plan_status: "reviewed"
script_status: "not-generated"
environment_variables:
  - LIMAS_BASE_URL
test_data: {}
related_script: ""
---

# Purpose

Verify that clicking the Sign In button navigates the user to the Keycloak authentication page.

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.

# Test Data

Use environment variables and runtime fixtures.

# Steps and Expected Results

1. Action: Navigate to `${LIMAS_BASE_URL}`.
   Expected Result: Login page loads with Sign In button visible.

2. Action: Click the Sign In button.
   Expected Result: Browser navigates to the Keycloak OpenID Connect authorization endpoint.

3. Action: Inspect the page after navigation.
   Expected Result: Keycloak login page is displayed with heading "Sign in to your account".

# Network Verification

- Request URL: Keycloak authorization endpoint (sanitized)
- HTTP Method: GET (redirect)
- Expected Status: 200
- Payload Presence: Keycloak login form
- Visible UI Result: Keycloak "Sign in to your account" heading visible

# Expected Final Result

After clicking Sign In, the browser navigates to the Keycloak login page showing the "Sign in to your account" heading.

# Classification

- Read-only
- Positive

# Restrictions

- Do not include credentials, tokens, cookies, authorization codes, or sensitive payloads.
- Do not capture PKCE or state parameters.
- Do not use static environment-specific data.

# Generation Status

- Test script generation: Pending
- CI/CD execution: Pending
- Healing: Pending