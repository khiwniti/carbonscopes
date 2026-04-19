# E2E Test Report - April 19, 2026

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | 43 |
| Passed | 6 (14%) |
| Failed | 36 (84%) |
| Skipped | 1 (2%) |
| Duration | ~6 minutes |

## Passing Tests ✅

| Test File | Test Name |
|-----------|-----------|
| `chat-simple.spec.ts` | simple chat test |
| `chat-full-test.spec.ts` | full chat test with carbon credit report |
| `compatibility.spec.ts` | backend health endpoint responds |
| `compatibility.spec.ts` | backend OpenAPI spec is accessible |
| `compatibility.spec.ts` | security headers configured |
| `infrastructure.spec.ts` | infrastructure: auth fixture produces valid auth state file |

## Root Cause Analysis

### 1. Console Error Monitoring Tests (12 failures) - FIXED
- **Cause**: Test using wrong port (3002 instead of 3001)
- **Fix**: Updated `e2e/console-error-monitor.spec.ts` line 8

### 2. React Hydration Errors (Multiple tests)
- **Symptom**: Console shows React hydration mismatch warnings
- **Root Cause**: React 19 + Next.js 15 hydration issues during dev mode
- **Impact**: Tests that check for console errors fail due to hydration warnings

### 3. Auth/Protected Route Tests (15 failures)
- **Cause**: Console error check fails due to hydration warnings
- **Secondary**: Auth state management in test fixtures needs review

### 4. Chat Input Timeout Tests (4 failures)
- **Cause**: Textarea not ready within 30s timeout
- **Likely**: Hydration delays or async component loading

## Test Files Status

| Test File | Tests | Passed | Failed | Notes |
|-----------|-------|--------|--------|-------|
| `chat-simple.spec.ts` | 1 | 1 | 0 | ✅ Working |
| `chat-full-test.spec.ts` | 1 | 1 | 0 | ✅ Working |
| `compatibility.spec.ts` | 9 | 3 | 5 | Mixed results |
| `infrastructure.spec.ts` | 5 | 1 | 4 | Auth fixture works |
| `console-error-monitor.spec.ts` | 12 | 0 | 12 | Port fixed, re-run needed |
| `dashboard.spec.ts` | 4 | 0 | 4 | Console error check |
| `projects.spec.ts` | 3 | 0 | 3 | Console error check |
| `chat-debug.spec.ts` | 1 | 0 | 1 | Timeout |
| `chat-carbon-report.spec.ts` | 2 | 0 | 2 | Timeout |
| `chat-test.spec.ts` | 2 | 0 | 2 | Timeout |
| `chat-with-auth.spec.ts` | 1 | 0 | 1 | Console errors |

## Recommendations

### Immediate Fixes
1. ✅ Fix port mismatch in console-error-monitor.spec.ts (done)
2. **Filter hydration warnings** from console error checks
3. **Increase timeout** for chat input tests

### Short-term
4. Add hydration error suppression in test environment
5. Review auth fixture reliability
6. Stabilize async component loading

### Commands

```bash
# Re-run tests after fixes
cd apps/frontend
pnpm test:e2e

# Run specific test file
npx playwright test chat-simple.spec.ts

# Run with UI for debugging
npx playwright test --ui

# View report
npx playwright show-report e2e-report
```

## Next Steps

1. Re-run E2E tests to verify port fix
2. If hydration warnings persist, update `checkConsoleErrors()` to filter them
3. Focus on getting core user journeys (chat, auth) stable
