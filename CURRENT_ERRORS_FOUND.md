# Current Errors Found - April 7, 2026

## Summary
Investigation of actual backend logs and server state reveals **1 CRITICAL error that MUST be fixed immediately**, and **3 MEDIUM errors previously marked as fixed but unclear if resolved**.

---

## 🔴 CRITICAL: Frontend Dependencies Not Installed

**Status:** BLOCKING - Frontend cannot run
**Location:** `/apps/frontend`
**Root Cause:** Dependencies not installed AND wrong package manager being used
**Error Message:** `sh: 1: next: not found` + `EUNSUPPORTEDPROTOCOL: workspace:*`
**Evidence:** `/apps/frontend/frontend.log`

### Details
**Problem 1:** npm cannot handle workspace protocols
```
npm error code EUNSUPPORTEDPROTOCOL
npm error Unsupported URL Type "workspace:": workspace:*
```

**Problem 2:** Missing dependencies
```
npm error: command sh -c next dev
npm error: sh: 1: next: not found
npm error code 127
```

### Root Cause Analysis
- This is a **pnpm monorepo** (see root `package.json` lines 5-7)
- Root package.json uses `pnpm --filter` commands
- Frontend uses `workspace:*` protocol for local dependencies
- npm does NOT support `workspace:*` protocol
- **Solution:** Use `pnpm` instead of `npm`

### Impact
- ❌ Frontend cannot start (`npm run dev` fails)
- ❌ All frontend routes inaccessible
- ❌ Cannot test or verify any frontend fixes

### Fix Required
Use pnpm (already installed - version 10.32.1):
```bash
cd /workspaces/carbonscopes
pnpm install
# OR for frontend only:
pnpm --filter carbonscope-frontend install
```

**Type:** Infrastructure/Setup Issue + Package Manager Mismatch
**File:** `/apps/frontend/package.json`, root `package.json`
**Priority:** CRITICAL

---

## 🟡 MEDIUM: Performance Timeouts (Unclear if Fixed)

According to ALL_ISSUES_FIXED.md (dated March 28), three medium issues were supposedly fixed:

### Issue 1: /berlin Route Timeout
- **Expected Fix:** Added loading states/optimization
- **Current State:** UNKNOWN - needs testing
- **Status:** Cannot verify without running frontend

### Issue 2: /credits-explained Route Timeout  
- **Expected Fix:** Same as /berlin
- **Current State:** UNKNOWN - needs testing
- **Status:** Cannot verify without running frontend

### Issue 3: /share/[threadId] Invalid ID Handling
- **Expected Fix:** Added validation & error UI (line 36 in share/[threadId]/page.tsx)
- **Current Code:** ✅ Validation present at line 36
- **Status:** Code appears correct, needs runtime testing

**All Verified In Code:**
- ✅ Error boundaries created: `/app/error.tsx`, `/app/(dashboard)/error.tsx`
- ✅ Share page validation: `/app/share/[threadId]/page.tsx`
- ✅ Error handling in API client

---

## ✅ Backend Status

**Health Check:** PASSING
```bash
curl http://localhost:8000/v1/health
# Returns: {"status":"ok",...}
```

**Import Fix:** ✅ VERIFIED (from previous session)
- Imports moved to top of api.py (lines 59-65)
- No undefined variables

**Error Handling:** ✅ VERIFIED
- Tests exist for error scenarios
- Proper 503/500 status codes
- No information leakage

---

## Next Steps

1. **IMMEDIATELY (Critical):** Install frontend dependencies
   ```bash
   cd apps/frontend && npm install
   ```

2. **VERIFY (Medium):** Test routes after frontend starts
   - Navigate to `/berlin` - check load time
   - Navigate to `/credits-explained` - check load time  
   - Navigate to `/share/invalid-id` - verify shows error

3. **MONITOR:** Check browser console for errors
   - JavaScript errors during page load
   - Network request errors
   - Performance warnings

