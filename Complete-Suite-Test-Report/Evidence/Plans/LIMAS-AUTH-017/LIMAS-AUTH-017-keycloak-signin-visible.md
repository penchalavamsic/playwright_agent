---
test_id: "LIMAS-AUTH-017"
title: "To verify the functionality of \"Keycloak\" → \"Sign In\" → \"Button visibility\""
module: "Keycloak"
page: "Keycloak login"
section: "Sign In"
control: "Sign In button"
action: "Visibility"
access_profile: "SUPER_USER_ADMIN_USER"
priority: "High"
classification: "Read-only"
test_type: "Visual"
automation_candidate: true
plan_status: "reviewed"
script_status: "not-generated"
environment_variables:
  - LIMAS_BASE_URL
test_data: {}
related_script: ""
---

# Purpose

Verify that the Keycloak Sign In button is visible on the login page.

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.

# Test Data

Use environment variables and runtime fixtures.

# Steps and Expected Results

1. Action: Navigate to `${LIMAS_BASE_URL}` and click Sign In.
   Expected Result: Keycloak login page loads.

2. Action: Look for the Sign In button.
   Expected Result: A button labeled "Sign In" is visible.

# Network Verification

- Request URL: Keycloak authorization endpoint (sanitized)
- HTTP Method: GET
- Expected Status: 200
- Payload Presence: Login form with Sign In button
- Visible UI Result: Sign In button visible

# Expected Final Result

The Keycloak Sign In button is visible.

# Classification

- Read-only
- Visual

# Restrictions

- Do not include credentials, tokens, cookies, authorization codes, or sensitive payloads.
- Do not use static environment-specific data.

# Generation Status

- Test script generation: Pending
- CI/CD execution: Pending
- Healing: Pending