# CarbonScope E2E Test Report

**URL:** https://carbonscope.ensimu.space/dashboard
**Date:** 2026-04-04
**Tester:** Hermes Agent

---

## Summary

| Category | Status | Details |
|----------|--------|---------|
| **Overall** | ⚠️ ISSUES FOUND | 1 Critical, 0 Important, 0 Minor |
| **Auth Flow** | ❌ FAILING | Magic link auth returns server error |
| **UI/UX** | ✅ PASS | Clean, modern design with good validation |
| **Console Errors** | ❌ FAILING | Auth error in console |

---

## Critical Issues (Must Fix)

### 1. Magic Link Authentication Fails

**Severity:** CRITICAL 🔴
**Component:** Authentication / Supabase Integration

**Steps to Reproduce:**
1. Navigate to https://carbonscope.ensimu.space/dashboard
2. Enter valid email: `test@example.com`
3. Check "I accept the Privacy Policy and Terms of Service"
4. Click "Send magic link"

**Expected:** Magic link email sent, success message displayed
**Actual:** Redirects to error page with "Authentication Error"

**Console Error:**
```javascript
{
  stack: "Error: An unexpected response was received from the server...",
  message: "An unexpected response was received from the server.",
  __NEXT_ERROR_CODE: "E394"
}
```

**Root Cause Analysis:**
- Likely Supabase email auth configuration issue
- Possible SMTP/email provider not configured
- Could be redirect URL mismatch in Supabase dashboard

**Recommended Fix:**
1. Check Supabase Dashboard > Authentication > URL Configuration
2. Verify Site URL matches `https://carbonscope.ensimu.space`
3. Check email templates and SMTP settings
4. Review Supabase auth logs for detailed error

---

## Tests Passed ✅

### 1. Login Page UI Rendering
- [x] Logo displays correctly
- [x] Heading "Sign in or create your CarbonScope account" visible
- [x] Google OAuth button present and styled
- [x] Email input field functional
- [x] Privacy Policy / Terms links present
- [x] "Send magic link" button present

### 2. Form Validation
- [x] Email field marked as required
- [x] Submit button disabled until checkbox checked
- [x] Submit button enables after checkbox checked
- [x] Email input accepts text input

### 3. Error Handling UX
- [x] Error page displays user-friendly message
- [x] "Try again" button available
- [x] "Go home" button available
- [x] Common causes listed for user guidance
- [x] Support email provided

### 4. Security Headers (from earlier review)
- [x] X-Frame-Options: SAMEORIGIN
- [x] X-Content-Type-Options: nosniff
- [x] Strict-Transport-Security enabled
- [x] HTTPS enforced

### 5. Console (Initial Load)
- [x] No JavaScript errors on page load
- [x] No console warnings on page load

---

## Tests Not Executed (Blocked by Auth)

| Test | Status | Reason |
|------|--------|--------|
| Dashboard functionality | ⏸️ BLOCKED | Cannot authenticate |
| Navigation menu | ⏸️ BLOCKED | Requires login |
| BIM file upload | ⏸️ BLOCKED | Requires login |
| Carbon analysis | ⏸️ BLOCKED | Requires login |
| Settings page | ⏸️ BLOCKED | Requires login |
| API endpoints | ⏸️ BLOCKED | Requires auth token |

---

## Screenshots

| Screenshot | Description |
|------------|-------------|
| `browser_screenshot_36308f1c...png` | Login page initial state |
| `browser_screenshot_71ef0533...png` | Authentication error page |

---

## Recommendations

### Immediate Actions (P0)
1. **Fix Supabase Auth** - Check Supabase dashboard for auth configuration
2. **Verify SMTP** - Ensure email provider is configured for magic links
3. **Check Redirect URLs** - Site URL in Supabase must match production domain

### Follow-up Actions (P1)
1. Add E2E tests with Playwright for auth flows
2. Implement auth error logging to backend
3. Add health check for Supabase connectivity
4. Consider fallback auth method if magic link fails

### Monitoring
1. Add error tracking (Sentry/PostHog) for auth failures
2. Monitor Supabase auth logs
3. Set up alerts for authentication error rates

---

## Environment

- **Browser:** Chromium (Browserbase)
- **Frontend:** Next.js 15 (standalone)
- **Auth:** Supabase Magic Link
- **Backend:** FastAPI on Azure
- **Domain:** carbonscope.ensimu.space

---

## Test Execution Log

```
10:33 - Navigate to /dashboard → Redirected to login
10:33 - Screenshot login page → PASS
10:33 - Check console errors → PASS (no errors)
10:34 - Enter email test@example.com → PASS
10:34 - Verify button disabled → PASS
10:34 - Check terms checkbox → PASS
10:34 - Verify button enabled → PASS
10:34 - Click "Send magic link" → FAIL
10:34 - Observe error page → Authentication Error
10:34 - Check console → ERROR: E394 unexpected response
10:34 - Screenshot error page → Captured
10:34 - Close browser → Complete
```

---

**Report Generated:** 2026-04-04T10:35:00Z
**Next Steps:** Fix Supabase authentication, then re-run full E2E suite
