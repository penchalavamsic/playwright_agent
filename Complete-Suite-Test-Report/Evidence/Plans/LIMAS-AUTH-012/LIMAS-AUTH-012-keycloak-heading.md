---
test_id: "LIMAS-AUTH-012"
title: "To verify the functionality of \"Keycloak\" → \"Login page\" → \"Heading visibility\""
module: "Keycloak"
page: "Keycloak login"
section: "Heading"
control: "Sign in heading"
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

Verify that the Keycloak login page displays the heading "Sign in to your account".

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.

# Test Data

Use environment variables and runtime fixtures.

# Steps and Expected Results

1. Action: Navigate to `${LIMAS_BASE_URL}` and click Sign In.
   Expected Result: Browser reaches the Keycloak login page.

2. Action: Inspect the page heading.
   Expected Result: A level-1 heading with text "Sign in to your account" is visible.

# Network Verification

- Request URL: Keycloak authorization endpoint (sanitized)
- HTTP Method: GET
- Expected Status: 200
- Payload Presence: Keycloak login form
- Visible UI Result: "Sign in to your account" heading

# Expected Final Result

The Keycloak page displays the heading "Sign in to your account".

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