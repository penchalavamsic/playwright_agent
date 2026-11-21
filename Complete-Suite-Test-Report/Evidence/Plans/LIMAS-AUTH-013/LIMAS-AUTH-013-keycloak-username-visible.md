---
test_id: "LIMAS-AUTH-013"
title: "To verify the functionality of \"Keycloak\" → \"Username or email\" → \"Field visibility\""
module: "Keycloak"
page: "Keycloak login"
section: "Username or email"
control: "Username field"
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

Verify that the Keycloak login form displays a "Username or email" text input field.

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.

# Test Data

Use environment variables and runtime fixtures.

# Steps and Expected Results

1. Action: Navigate to `${LIMAS_BASE_URL}` and click Sign In.
   Expected Result: Keycloak login page loads.

2. Action: Look for the username input field.
   Expected Result: A textbox labeled "Username or email" is visible.

# Network Verification

- Request URL: Keycloak authorization endpoint (sanitized)
- HTTP Method: GET
- Expected Status: 200
- Payload Presence: Login form with username field
- Visible UI Result: "Username or email" textbox visible

# Expected Final Result

The "Username or email" textbox is visible on the Keycloak page.

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