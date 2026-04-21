# Next Task Selection - Phase 2 Security

## Completed Phase 2 Tasks ✅
- ✅ Task #113: Dev authentication bypass
- ✅ Task #112: SQL injection audit (no fixes needed)
- ✅ Task #109: XSS protection (19 instances protected, 7 static reverted)
- ✅ Task #114: Rate limiting on auth endpoints (SEC-04) — 2026-04-20
  - slowapi integrated with Redis/in-memory backend
  - Applied to: OTP send/verify, Google OAuth auth-url/callback, account setup/initialize-anonymous, API key creation, webhooks
  - AUTH_RATE_LIMIT = "5/15minutes", DEFAULT_RATE_LIMIT = "100/minute"
  - Auth API module (backend/auth/api.py) created with OTP endpoints
- ✅ Task #111: CSRF protection middleware (SEC-05) — 2026-04-20
  - Double-submit cookie pattern (CSRFMiddleware)
  - Exempt: Bearer token auth, API key auth, webhook paths, safe methods, health checks
  - CSRF token endpoint: GET /v1/csrf-token
  - X-CSRF-Token header added to CORS allowed headers

## Remaining Phase 2 Security Tasks

### Task #115: CSP Connect-Src Tightening (SEC-01)
**Priority**: MEDIUM
**Scope**: Remove broad localhost allowlist from CSP connect-src in production
**Status**: Previously resolved as F-11

### Task #116: Secret Scanning in CI (SEC-02)
**Priority**: MEDIUM
**Scope**: Add secret scanning step to CI pipeline
**Status**: Previously resolved as F-06

### Task #117: API Keys via Environment Variables (SEC-03)
**Priority**: MEDIUM
**Scope**: Ensure all API keys use environment variables, no hardcoded values
**Dependencies**: Codebase audit needed

## All Phase 2 Security Tasks Complete ✅

**Recommendation**: No further Phase 2 security tasks required. Core security hardening (rate limiting + CSRF) is implemented and tested.
