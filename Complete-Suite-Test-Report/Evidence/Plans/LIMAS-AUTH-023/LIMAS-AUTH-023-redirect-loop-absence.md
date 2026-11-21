---
test_id: "LIMAS-AUTH-023"
title: "To verify the functionality of \"Authentication\" → \"Session\" → \"Redirect loop absence\""
module: "Authentication"
page: "All authenticated pages"
section: "Session"
control: "Redirect behavior"
action: "Loop absence"
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

Verify that the authentication flow does not create a redirect loop between the application and Keycloak.

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.
- Valid credentials for `SUPER_USER_ADMIN_USER` are configured.

# Test Data

Credential variable names from the profile are read at runtime.

# Steps and Expected Results

1. Action: Navigate to `${LIMAS_BASE_URL}` and complete full Keycloak login.
   Expected Result: User lands on the System User Dashboard.

2. Action: After reaching the dashboard, observe URL for a period.
   Expected Result: The URL does not bounce back to `/login` or the Keycloak authorization endpoint.

# Network Verification

- Request URL: `/system-user-dashboard`
- HTTP Method: GET
- Expected Status: 200
- Payload Presence: Stable dashboard
- Visible UI Result: No redirect loop detected

# Expected Final Result

No redirect loop occurs after successful authentication.

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