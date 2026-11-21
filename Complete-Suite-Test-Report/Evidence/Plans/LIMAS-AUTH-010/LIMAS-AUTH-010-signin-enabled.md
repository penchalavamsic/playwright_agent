---
test_id: "LIMAS-AUTH-010"
title: "To verify the functionality of \"Authentication\" → \"Login page\" → \"Sign In button\" → \"Enabled state\""
module: "Authentication"
page: "Login page"
section: "Sign In button"
control: "Sign In button"
action: "Enabled state"
access_profile: "SUPER_USER_ADMIN_USER"
priority: "High"
classification: "Read-only"
test_type: "Positive"
automation_candidate: true
plan_status: "reviewed"
script_status: "not-generated"
environment_variables:
  - LIMAS_BASE_URL
test_data: {}
related_script: ""
---

# Purpose

Verify that the Sign In button on the LIMAS login page is enabled and clickable.

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.

# Test Data

Use environment variables and runtime fixtures.

# Steps and Expected Results

1. Action: Navigate to `${LIMAS_BASE_URL}`.
   Expected Result: Login page loads.

2. Action: Locate the Sign In button.
   Expected Result: The button is visible and not disabled.

# Network Verification

- Request URL: `${LIMAS_BASE_URL}/`
- HTTP Method: GET
- Expected Status: 200
- Payload Presence: Login page rendered
- Visible UI Result: Sign In button enabled

# Expected Final Result

The Sign In button is in an enabled state.

# Classification

- Read-only
- Positive

# Restrictions

- Do not include credentials, tokens, cookies, authorization codes, or sensitive payloads.
- Do not use static environment-specific data.

# Generation Status

- Test script generation: Pending
- CI/CD execution: Pending
- Healing: Pending