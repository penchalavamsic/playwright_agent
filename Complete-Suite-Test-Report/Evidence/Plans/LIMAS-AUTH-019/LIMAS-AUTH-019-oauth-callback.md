---
test_id: "LIMAS-AUTH-019"
title: "To verify the functionality of \"Authentication\" → \"OAuth\" → \"Callback completion\""
module: "Authentication"
page: "OAuth callback"
section: "OAuth"
control: "Callback handler"
action: "Completion"
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

Verify that after valid Keycloak credential submission, the OAuth callback completes and redirects to the application.

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.
- Valid `${LIMAS_SUPER_USER_ADMIN_USER_USERNAME}` and `${LIMAS_SUPER_USER_ADMIN_USER_PASSWORD}` are configured in `.env`.
- Access profile `SUPER_USER_ADMIN_USER` is configured in `access-profiles.json`.

# Test Data

Credential variable names from the `SUPER_USER_ADMIN_USER` profile are read at runtime.

# Steps and Expected Results

1. Action: Navigate to `${LIMAS_BASE_URL}`, click Sign In.
   Expected Result: Keycloak login page loads.

2. Action: Fill username and password from profile, click Keycloak Sign In.
   Expected Result: Browser processes OAuth callback at `/auth/callback`.

3. Action: Wait for final redirect.
   Expected Result: Browser lands on `/system-user-dashboard`.

# Network Verification

- Request URL: `/auth/callback` (sanitized query params)
- HTTP Method: GET
- Expected Status: 200 → redirect
- Payload Presence: OAuth redirect response
- Visible UI Result: System User Dashboard loads

# Expected Final Result

The OAuth callback completes and redirects to the System User Dashboard.

# Classification

- Read-only
- Session

# Restrictions

- Do not include credentials, tokens, cookies, authorization codes, or sensitive payloads.
- Do not capture authorization-code or state parameters.
- Do not use static environment-specific data.

# Generation Status

- Test script generation: Pending
- CI/CD execution: Pending
- Healing: Pending