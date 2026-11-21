---
test_id: "LIMAS-AUTH-021"
title: "To verify the functionality of \"Authentication\" → \"Session\" → \"Authenticated route stability\""
module: "Authentication"
page: "System User Dashboard"
section: "Session"
control: "Route"
action: "Stability"
access_profile: "SUPER_USER_ADMIN_USER"
priority: "Critical"
classification: "Read-only"
test_type: "Session"
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

Verify that the authenticated dashboard remains at the correct route after login without redirect loops.

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.
- Valid credentials for `SUPER_USER_ADMIN_USER` are configured.

# Test Data

Credential variable names from the profile are read at runtime.

# Steps and Expected Results

1. Action: Complete full Keycloak login and redirect to the dashboard.
   Expected Result: Final URL is `/system-user-dashboard`.

2. Action: Wait and observe for any redirect loops or unexpected navigation.
   Expected Result: The route remains stable at `/system-user-dashboard` without loops.

# Network Verification

- Request URL: `/system-user-dashboard`
- HTTP Method: GET
- Expected Status: 200
- Payload Presence: Dashboard content
- Visible UI Result: Stable dashboard with no redirect loops

# Expected Final Result

The authenticated session remains stable at `/system-user-dashboard` without redirect loops.

# Classification

- Read-only
- Session

# Restrictions

- Do not include credentials, tokens, cookies, authorization codes, or sensitive payloads.
- Do not use static environment-specific data.

# Generation Status

- Test script generation: Pending
- CI/CD execution: Pending
- Healing: Pending