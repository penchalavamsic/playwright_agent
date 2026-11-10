---
test_id: ""
title: ""
module: ""
page: ""
section: ""
control: ""
action: ""
access_profile: ""
priority: ""
classification: ""
test_type: ""
automation_candidate: true
plan_status: "draft"
script_status: "not-generated"
environment_variables: []
test_data: {}
related_script: ""
---

# Purpose

Describe the single small behavior being verified.

# Preconditions

- `${LIMAS_BASE_URL}` is reachable.
- Credentials for `${TEST_ACCESS_PROFILE}` are configured.
- The required role and test data are available.
- The starting page is accessible.

# Test Data

Use environment variables, runtime fixtures, or configuration keys.

# Steps and Expected Results

1. Action:
   Expected Result:

2. Action:
   Expected Result:

# Network Verification

- Request URL:
- HTTP Method:
- Expected Status:
- Payload Presence:
- Visible UI Result:

# Expected Final Result

Describe one clear and independently verifiable result.

# Classification

- Read-only or Data-changing
- Positive, Negative, Boundary, Permission, Visual, API, Accessibility, or Session

# Restrictions

- Do not include credentials, tokens, cookies, authorization codes, or sensitive payloads.
- Do not repeat data-changing submissions.
- Do not manually navigate to simulate a successful result.
- Do not use static environment-specific data.

# Generation Status

- Test script generation: Pending
- CI/CD execution: Pending
- Healing: Pending

# Dynamic Plan Rules

1. Use only behavior verified through Playwright MCP.
2. Verify one atomic behavior per plan.
3. Do not hardcode application URLs.
4. Do not hardcode usernames or passwords.
5. Do not hardcode user names, emails, request IDs, license IDs, hardware IDs, dates, User Groups, Profiles, Roles, feature names, versions, or local paths.
6. Use environment variables, access-profiles.json, runtime fixtures, or test-data configuration.
7. Select exactly one access profile:
   - SUPER_USER
   - ADMIN
   - SUPER_USER_ADMIN_USER
8. Keep every plan shareable between environments and team members.
9. CI/CD owns test execution.
10. The Healer may propose test-only changes later but must not change expected LIMAS behavior.
11. Plans must use this Jira-style title format:

To verify the functionality of "<Module>" → "<Section>" → "<Control>" → "<Action>"