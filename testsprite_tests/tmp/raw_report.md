
# TestSprite AI Testing Report(MCP)

---

## 1️⃣ Document Metadata
- **Project Name:** carbonscopes
- **Date:** 2026-04-21
- **Prepared by:** TestSprite AI Team

---

## 2️⃣ Requirement Validation Summary

#### Test TC001 get_v1_health_should_return_status_ok
- **Test Code:** [TC001_get_v1_health_should_return_status_ok.py](./TC001_get_v1_health_should_return_status_ok.py)
- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0dad88fe-2701-4898-91e5-ecc84dceaeb5/3c8ed99b-c787-4f02-9c4a-fffef06dc525
- **Status:** ✅ Passed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC002 post_v1_auth_otp_send_should_send_magic_link_and_respect_rate_limit
- **Test Code:** [TC002_post_v1_auth_otp_send_should_send_magic_link_and_respect_rate_limit.py](./TC002_post_v1_auth_otp_send_should_send_magic_link_and_respect_rate_limit.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 58, in <module>
  File "<string>", line 26, in test_post_v1_auth_otp_send_should_send_magic_link_and_respect_rate_limit
AssertionError: Expected 200 OK on attempt 1, got 429. Response body: {"error":"rate_limit_exceeded","message":"Too many requests. Please try again later.","retry_after":"unknown"}

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0dad88fe-2701-4898-91e5-ecc84dceaeb5/e0925756-564b-4058-a94a-8bb47615a5d5
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC003 post_v1_auth_otp_verify_should_validate_token_and_handle_invalid_tokens
- **Test Code:** [TC003_post_v1_auth_otp_verify_should_validate_token_and_handle_invalid_tokens.py](./TC003_post_v1_auth_otp_verify_should_validate_token_and_handle_invalid_tokens.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 74, in <module>
  File "<string>", line 22, in test_post_v1_auth_otp_verify_should_validate_token_and_handle_invalid_tokens
AssertionError: OTP send failed with status 500

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0dad88fe-2701-4898-91e5-ecc84dceaeb5/f4c17767-41f5-49bb-aa4d-b6685f703640
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC004 get_v1_csrf_token_should_set_csrf_token_cookie
- **Test Code:** [TC004_get_v1_csrf_token_should_set_csrf_token_cookie.py](./TC004_get_v1_csrf_token_should_set_csrf_token_cookie.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 28, in <module>
  File "<string>", line 26, in test_get_v1_csrf_token_should_set_csrf_token_cookie
AssertionError: csrf_token cookie not set in response

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0dad88fe-2701-4898-91e5-ecc84dceaeb5/9db8b973-5896-407f-a313-4099ba2175c1
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC005 post_v1_api_keys_should_create_api_key_for_authenticated_user
- **Test Code:** [TC005_post_v1_api_keys_should_create_api_key_for_authenticated_user.py](./TC005_post_v1_api_keys_should_create_api_key_for_authenticated_user.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 2, in <module>
ModuleNotFoundError: No module named 'pytest'

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0dad88fe-2701-4898-91e5-ecc84dceaeb5/e56d1c9c-b27d-4590-906c-42a8bca10160
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC006 post_v1_initialize_should_initialize_authenticated_user_account
- **Test Code:** [TC006_post_v1_initialize_should_initialize_authenticated_user_account.py](./TC006_post_v1_initialize_should_initialize_authenticated_user_account.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 81, in <module>
  File "<string>", line 20, in test_post_v1_initialize_should_initialize_authenticated_user_account
AssertionError: OTP send failed: 429 {"error":"rate_limit_exceeded","message":"Too many requests. Please try again later.","retry_after":"unknown"}

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0dad88fe-2701-4898-91e5-ecc84dceaeb5/9f35d8e6-d12f-43d0-a684-9e3f82b7ce9b
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC007 post_v1_initialize_anonymous_should_create_anonymous_account_and_enforce_rate_limit
- **Test Code:** [TC007_post_v1_initialize_anonymous_should_create_anonymous_account_and_enforce_rate_limit.py](./TC007_post_v1_initialize_anonymous_should_create_anonymous_account_and_enforce_rate_limit.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 51, in <module>
  File "<string>", line 42, in test_post_v1_initialize_anonymous_should_create_anonymous_account_and_enforce_rate_limit
AssertionError: Unexpected HTTP status 404 on attempt 1

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0dad88fe-2701-4898-91e5-ecc84dceaeb5/383ec638-9d6f-4182-aec8-54266f12821b
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC008 post_v1_carbon_calculate_should_return_carbon_footprint_or_bad_request
- **Test Code:** [TC008_post_v1_carbon_calculate_should_return_carbon_footprint_or_bad_request.py](./TC008_post_v1_carbon_calculate_should_return_carbon_footprint_or_bad_request.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 54, in <module>
  File "<string>", line 35, in test_post_v1_carbon_calculate_should_return_carbon_footprint_or_bad_request
AssertionError: Expected 200 OK, got 404

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0dad88fe-2701-4898-91e5-ecc84dceaeb5/962522f7-7f6a-4ad2-bda3-28f8a3b67e99
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC009 post_v1_agent_start_should_start_agent_run_for_authenticated_user
- **Test Code:** [TC009_post_v1_agent_start_should_start_agent_run_for_authenticated_user.py](./TC009_post_v1_agent_start_should_start_agent_run_for_authenticated_user.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 45, in <module>
  File "<string>", line 32, in test_post_v1_agent_start_should_start_agent_run_for_authenticated_user
AssertionError: Unexpected status code 401, Response: {"detail":"Invalid token format"}

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0dad88fe-2701-4898-91e5-ecc84dceaeb5/98cd1739-0858-4a03-978d-d8cc5b9068c7
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---

#### Test TC010 post_v1_threads_should_create_thread_with_csrf_protection_and_authentication
- **Test Code:** [TC010_post_v1_threads_should_create_thread_with_csrf_protection_and_authentication.py](./TC010_post_v1_threads_should_create_thread_with_csrf_protection_and_authentication.py)
- **Test Error:** Traceback (most recent call last):
  File "/var/task/handler.py", line 258, in run_with_retry
    exec(code, exec_env)
  File "<string>", line 107, in <module>
  File "<string>", line 18, in test_post_v1_threads_should_create_thread_with_csrf_protection_and_authentication
AssertionError: OTP send failed: Internal Server Error

- **Test Visualization and Result:** https://www.testsprite.com/dashboard/mcp/tests/0dad88fe-2701-4898-91e5-ecc84dceaeb5/c68dc707-ee5d-4595-8f21-780fdd3d4178
- **Status:** ❌ Failed
- **Analysis / Findings:** {{TODO:AI_ANALYSIS}}.
---


## 3️⃣ Coverage & Matching Metrics

- **10.00** of tests passed

| Requirement        | Total Tests | ✅ Passed | ❌ Failed  |
|--------------------|-------------|-----------|------------|
| ...                | ...         | ...       | ...        |
---


## 4️⃣ Key Gaps / Risks
{AI_GNERATED_KET_GAPS_AND_RISKS}
---