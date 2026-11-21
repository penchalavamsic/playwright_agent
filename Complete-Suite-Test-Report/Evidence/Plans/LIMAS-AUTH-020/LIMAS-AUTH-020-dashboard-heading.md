---
test_id: "LIMAS-AUTH-020"
title: "To verify the functionality of \"Authentication\" → \"Role routing\" → \"System User Dashboard heading\""
module: "Authentication"
page: "System User Dashboard"
section: "Heading"
control: "Dashboard heading"
action: "Visibility"
access_profile: "SUPER_USER_ADMIN_USER"
priority: "Critical"
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

Verify that after successful SUPER_USER_ADMIN_USER login, the System User Dashboard heading is visible.

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.
- Valid credentials for `SUPER_USER_ADMIN_USER` are configured.

# Test Data

Credential variable names from the profile are read at runtime.

# Steps and Expected Results

1. Action: Navigate to `${LIMAS_BASE_URL}`, click Sign In, and complete Keycloak login with `SUPER_USER_ADMIN_USER` credentials.
   Expected Result: Browser redirects to `/system-user-dashboard`.

2. Action: Inspect the page heading.
   Expected Result: A level-1 heading with text "System User Dashboard" is visible.

# Network Verification

- Request URL: `/system-user-dashboard`
- HTTP Method: GET
- Expected Status: 200
- Payload Presence: Dashboard page
- Visible UI Result: "System User Dashboard" heading visible

# Expected Final Result

The "System User Dashboard" heading is displayed on the page.

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