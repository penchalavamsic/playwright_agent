---
test_id: "LIMAS-AUTH-009"
title: "To verify the functionality of \"Authentication\" → \"Login page\" → \"Branding visibility\""
module: "Authentication"
page: "Login page"
section: "Branding"
control: "KPIT and LIMAS logos"
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

Verify that the LIMAS login page displays both KPIT and LIMAS branding logos.

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.

# Test Data

Use environment variables and runtime fixtures.

# Steps and Expected Results

1. Action: Navigate to `${LIMAS_BASE_URL}`.
   Expected Result: The page loads at the login route.

2. Action: Inspect the branding area.
   Expected Result: The KPIT Logo image and LIMAS Logo image are both visible.

# Network Verification

- Request URL: `${LIMAS_BASE_URL}/`
- HTTP Method: GET
- Expected Status: 200
- Payload Presence: KPIT and LIMAS logo SVGs loaded
- Visible UI Result: Two logo images rendered

# Expected Final Result

The login page displays both KPIT and LIMAS logo images.

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