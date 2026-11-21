---
test_id: "LIMAS-AUTH-022"
title: "To verify the functionality of \"Authentication\" → \"Session\" → \"Page refresh persistence\""
module: "Authentication"
page: "System User Dashboard"
section: "Session"
control: "Page refresh"
action: "Persistence"
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

Verify that the authenticated session persists across a full page refresh.

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.
- Valid credentials for `SUPER_USER_ADMIN_USER` are configured.

# Test Data

Credential variable names from the profile are read at runtime.

# Steps and Expected Results

1. Action: Complete full Keycloak login and confirm the dashboard loads.
   Expected Result: System User Dashboard is visible.

2. Action: Refresh the page.
   Expected Result: The dashboard reloads without returning to the login page.

3. Action: Verify the dashboard heading after refresh.
   Expected Result: "System User Dashboard" heading is still visible and content is rendered.

# Network Verification

- Request URL: `/system-user-dashboard`
- HTTP Method: GET
- Expected Status: 200
- Payload Presence: Dashboard content
- Visible UI Result: Dashboard rendered after refresh

# Expected Final Result

The authenticated dashboard persists across a page refresh.

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