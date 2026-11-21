---
test_id: "LIMAS-AUTH-026"
title: "To verify the functionality of \"Authentication\" → \"Post-login\" → \"User button visibility\""
module: "Authentication"
page: "System User Dashboard"
section: "Header"
control: "User button"
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
  - LIMAS_SUPER_USER_ADMIN_USER_USERNAME
  - LIMAS_SUPER_USER_ADMIN_USER_PASSWORD
test_data: {}
related_script: ""
---

# Purpose

Verify that after login, the header displays a user-identity button indicating the logged-in user.

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.
- Valid credentials for `SUPER_USER_ADMIN_USER` are configured.

# Test Data

Credential variable names from the profile are read at runtime.

# Steps and Expected Results

1. Action: Complete full Keycloak login and reach the dashboard.
   Expected Result: System User Dashboard is visible.

2. Action: Inspect the header for user-identity elements.
   Expected Result: A button showing the user's initial(s) or identifier is visible in the header.

# Network Verification

- Request URL: `/system-user-dashboard`
- HTTP Method: GET
- Expected Status: 200
- Payload Presence: Dashboard with header
- Visible UI Result: User button visible in header

# Expected Final Result

A user-identity button is visible in the dashboard header.

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