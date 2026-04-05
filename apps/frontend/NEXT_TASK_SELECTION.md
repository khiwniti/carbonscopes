# Next Task Selection - Phase 2 Security

## Completed Phase 2 Tasks ✅
- ✅ Task #113: Dev authentication bypass
- ✅ Task #112: SQL injection audit (no fixes needed)
- ✅ Task #109: XSS protection (19 instances protected, 7 static reverted)

## Remaining Phase 2 Security Tasks

### Task #114: Implement Rate Limiting on Auth Endpoints
**Priority**: HIGH (prevents brute force attacks)
**Scope**: 
- Install slowapi or similar for FastAPI
- Target endpoints: /auth/magic-link, /auth/oauth, /api/keys
- Limit: 5 attempts per 15 minutes per IP
**Complexity**: MODERATE (requires backend changes + testing)
**Dependencies**: None

### Task #111: Add CSRF Protection
**Priority**: HIGH (prevents cross-site request forgery)
**Scope**: 
- Add CSRF token validation
- All POST/PUT/DELETE endpoints
- Exemptions: API endpoints with proper auth
**Complexity**: MODERATE (requires middleware + frontend integration)
**Dependencies**: None

## Recommendation: Task #114 (Rate Limiting)

**Rationale**:
1. Simpler implementation (backend-only)
2. Immediate security benefit (prevents brute force)
3. No frontend integration required
4. Can be tested with curl
5. Sets foundation for CSRF protection (both are middleware-based)

**Next Step**: Dispatch implementer for Task #114
