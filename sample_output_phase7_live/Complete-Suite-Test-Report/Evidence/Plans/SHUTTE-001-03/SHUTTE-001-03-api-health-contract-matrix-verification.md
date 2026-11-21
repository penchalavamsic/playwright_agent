---
test_id: "SHUTTE-001-03"
title: "To verify the functionality of \"Shutterstock\" → \"Shutterstock Studio Portal\" → \"API Health & Contract Matrix Verification\""
module: "Shutterstock"
page: "Shutterstock Studio Portal"
section: "Primary Flow"
control: "Interactive Controls"
action: "Execution & Verification"
access_profile: "SUPER_USER"
priority: "High"
classification: "Read-only"
test_type: "Positive"
automation_candidate: true
plan_status: "reviewed"
script_status: "generated"
environment_variables:
  - BASE_URL
  - TEST_ACCESS_PROFILE
test_data: {}
related_script: "tests/api-health-contract-matrix-verification.spec.ts"
---

# Purpose

Verify the functionality of "Shutterstock" → "Shutterstock Studio Portal" → "API Health & Contract Matrix Verification" under access profile `SUPER_USER`.

# Preconditions

- `${BASE_URL}` is reachable.
- Credentials for `${TEST_ACCESS_PROFILE}` (`SUPER_USER`) are configured in `.env`.

# Test Data

Use environment variables and runtime fixtures.

# Steps and Expected Results

1. Action: Validate contract for GET /api/search (Expected Status: [200], Keys: ['status', 'results']).
   Expected Result: Step completes deterministically without UI or network errors.

# Network Verification

- Request URL: `${BASE_URL}/api/search`
- HTTP Method: GET
- Expected Status: 200
- Payload Presence: Verified response payload
- Visible UI Result: Interactive controls visible and responsive

# Expected Final Result

All steps and network status assertions succeed for SHUTTE-001-03.

# Classification

- Read-only
- Positive

# Restrictions

- Do not include credentials, tokens, cookies, authorization codes, or sensitive payloads.
- Do not use static environment-specific data.

# Generation Status

- Test script generation: Complete
- CI/CD execution: Ready
- Healing: Ready
