---
test_id: "LIMAS-AUTH-024"
title: "To verify the functionality of \"Authentication\" → \"Login page\" → \"Footer visibility\""
module: "Authentication"
page: "Login page"
section: "Footer"
control: "Copyright notice"
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

Verify that the LIMAS login page footer displays the KPIT copyright notice.

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.

# Test Data

Use environment variables and runtime fixtures.

# Steps and Expected Results

1. Action: Navigate to `${LIMAS_BASE_URL}`.
   Expected Result: Login page loads.

2. Action: Inspect the footer area.
   Expected Result: Text "© KPIT Technologies Ltd. All rights reserved." is visible.

# Network Verification

- Request URL: `${LIMAS_BASE_URL}/`
- HTTP Method: GET
- Expected Status: 200
- Payload Presence: Login page with footer
- Visible UI Result: Copyright notice visible

# Expected Final Result

The KPIT copyright notice is visible in the footer of the login page.

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