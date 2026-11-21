---
test_id: "LIMAS-AUTH-016"
title: "To verify the functionality of \"Keycloak\" → \"Password\" → \"Masked state\""
module: "Keycloak"
page: "Keycloak login"
section: "Password"
control: "Password field"
action: "Masked state"
access_profile: "SUPER_USER_ADMIN_USER"
priority: "Critical"
classification: "Read-only"
test_type: "Security"
automation_candidate: true
plan_status: "reviewed"
script_status: "not-generated"
environment_variables:
  - LIMAS_BASE_URL
test_data: {}
related_script: ""
---

# Purpose

Verify that the Password field on the Keycloak login page masks entered text by default.

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.

# Test Data

Use environment variables and runtime fixtures.

# Steps and Expected Results

1. Action: Navigate to `${LIMAS_BASE_URL}` and click Sign In.
   Expected Result: Keycloak login page loads.

2. Action: Locate the Password field.
   Expected Result: The field has type "password" (masked). A "Show password" toggle button is also present.

# Network Verification

- Request URL: Keycloak authorization endpoint (sanitized)
- HTTP Method: GET
- Expected Status: 200
- Payload Presence: Login form
- Visible UI Result: Password field masked, Show password button visible

# Expected Final Result

The Password field masks entered characters by default and provides a Show password toggle.

# Classification

- Read-only
- Security

# Restrictions

- Do not include credentials, tokens, cookies, authorization codes, or sensitive payloads.
- Do not use static environment-specific data.

# Generation Status

- Test script generation: Pending
- CI/CD execution: Pending
- Healing: Pending