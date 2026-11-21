---
test_id: "LIMAS-AUTH-025"
title: "To verify the functionality of \"Authentication\" → \"Keycloak\" → \"Show password toggle\" → \"Visibility\""
module: "Keycloak"
page: "Keycloak login"
section: "Password"
control: "Show password button"
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

Verify that the Keycloak login form provides a "Show password" toggle button next to the Password field.

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.

# Test Data

Use environment variables and runtime fixtures.

# Steps and Expected Results

1. Action: Navigate to `${LIMAS_BASE_URL}` and click Sign In.
   Expected Result: Keycloak login page loads.

2. Action: Locate the Password field area.
   Expected Result: A "Show password" button is present adjacent to the Password textbox.

# Network Verification

- Request URL: Keycloak authorization endpoint (sanitized)
- HTTP Method: GET
- Expected Status: 200
- Payload Presence: Login form
- Visible UI Result: "Show password" button visible

# Expected Final Result

A "Show password" toggle button is visible next to the Password field.

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