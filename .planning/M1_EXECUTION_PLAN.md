# M1: Production Stability - Execution Plan

**Status:** READY TO EXECUTE
**Priority:** 🔴 CRITICAL
**Timeline:** 1-2 days

---

## 🎯 Objective

Fix all production errors blocking users and establish monitoring to prevent future issues.

---

## 📋 Phase 1: Critical Backend Fix (4-6 hours)

### Task 1.1: Get Backend Logs ⏱️ 15 min
**Owner:** You
**Tools:** Azure CLI

```bash
# Login to Azure
az login

# Find resource group
az webapp list --query "[?name=='suna-backend-app'].{name:name, rg:resourceGroup}" -o table

# Tail live logs
az webapp log tail --name suna-backend-app --resource-group <rg-from-above>

# Download logs for analysis
az webapp log download --name suna-backend-app --resource-group <rg-from-above> --log-file backend-logs.zip

# Extract and search for errors
unzip backend-logs.zip
grep -i "GET /v1/agents" */AppServiceAppLogs*.txt > .planning/agents_500_logs.txt
```

**Deliverable:** `.planning/agents_500_logs.txt` with Python traceback

---

### Task 1.2: Root Cause Analysis ⏱️ 30 min
**Owner:** GSD gsd-debugger agent
**Command:** `/gsd:debug`

**Analyze:**
1. Python exception type and message
2. Database query failures (Prisma/Supabase)
3. Authentication/authorization issues
4. Missing environment variables
5. Service dependencies (Redis, Supabase)

**Deliverable:** `.planning/phase1/ROOT_CAUSE.md`

---

### Task 1.3: Implement Fix ⏱️ 2-3 hours
**Owner:** GSD gsd-executor agent
**Command:** `/gsd:execute-phase phase1`

**Expected fixes:**
- Database schema migration if needed
- Fix Prisma query syntax
- Add error handling
- Update environment variables
- Fix Redis connection pooling

**Files to modify:**
- `apps/backend/routers/v1/agents.py`
- `apps/backend/core/agents/*.py`
- `apps/backend/prisma/schema.prisma` (if needed)

**Deliverable:** Working `/v1/agents` endpoint

---

### Task 1.4: Test & Deploy ⏱️ 30 min
**Owner:** You + Vercel CLI

```bash
# Test locally
cd apps/backend
uv run pytest tests/routers/test_agents.py -v

# Test endpoint manually
curl -X GET "http://localhost:8000/v1/agents?limit=50" \
  -H "Authorization: Bearer <test-token>"

# Deploy to Azure
az webapp deployment source sync \
  --name suna-backend-app \
  --resource-group <rg-name>

# Verify production
curl "https://suna-backend-app.azurewebsites.net/v1/agents?limit=50" \
  -H "Authorization: Bearer <prod-token>"
```

**Success criteria:**
- ✅ Returns HTTP 200
- ✅ Returns JSON array of agents
- ✅ Homepage shows agent list
- ✅ No 500 errors in console

---

## 📋 Phase 2: Frontend Cleanup (1 hour)

### Task 2.1: Fix GitHub Stars ⏱️ 30 min

**Option A - Quick Fix (5 min):**
```typescript
// File: apps/frontend/src/hooks/utils/use-github-stars.ts
// Line 31: Change error to debug
- console.error('Failed to fetch GitHub stars:', err);
+ console.debug('Failed to fetch GitHub stars:', err);
```

**Option B - Complete Fix (30 min):**
1. Verify correct repo: `https://github.com/CarbonScope-ai/suna` exists?
2. Update all references if repo path changed
3. OR remove GitHub stars feature entirely

**Files to check:**
- `apps/frontend/src/lib/site-config.ts`
- `apps/frontend/src/components/home/simple-footer.tsx`
- `apps/frontend/src/components/home/footer-section.tsx`

---

### Task 2.2: Deploy Frontend ⏱️ 15 min

```bash
# Deploy to Vercel
cd apps/frontend
vercel --prod

# Verify
open https://carbonscope.ensimu.space
# Check console - should be clean
```

---

## 📋 Phase 3: Monitoring Setup (2-3 hours)

### Task 3.1: Backend Error Tracking ⏱️ 1 hour

**Add Sentry to Backend:**
```python
# apps/backend/main.py
import sentry_sdk

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    environment="production",
    traces_sample_rate=0.1,
)
```

**Configure Azure Application Insights:**
```bash
az monitor app-insights component create \
  --app carbonscope-backend \
  --location eastus \
  --resource-group <rg-name>
```

---

### Task 3.2: Frontend Error Boundary ⏱️ 30 min

```typescript
// apps/frontend/src/app/error.tsx
'use client'
import * as Sentry from '@sentry/nextjs'

export default function Error({ error }: { error: Error }) {
  Sentry.captureException(error)
  return <ErrorFallback />
}
```

---

### Task 3.3: Health Dashboard ⏱️ 1 hour

**Create:** `apps/frontend/src/app/admin/health/page.tsx`

**Display:**
- Backend API status
- Database connectivity
- Redis connection
- Recent error count
- Response times (p50, p95, p99)

---

## 🚀 Deployment Checklist

### Pre-Deploy
- [ ] All tests passing locally
- [ ] Backend logs show no errors
- [ ] Environment variables verified
- [ ] Database migrations applied

### Deploy Backend
```bash
az webapp deployment source sync \
  --name suna-backend-app \
  --resource-group <rg-name>
```

### Deploy Frontend
```bash
vercel --prod
```

### Post-Deploy Verification
- [ ] Visit https://carbonscope.ensimu.space
- [ ] Check browser console (should be clean)
- [ ] Test agent selection workflow
- [ ] Verify no 500 errors
- [ ] Check error tracking dashboard

---

## 📊 Success Metrics

**Phase 1 Complete:**
- ✅ `/v1/agents` returns HTTP 200
- ✅ Users can list agents
- ✅ Users can create projects
- ✅ Zero backend 500 errors

**Phase 2 Complete:**
- ✅ Clean browser console
- ✅ No GitHub API errors
- ✅ All links functional

**Phase 3 Complete:**
- ✅ Error tracking configured
- ✅ Health dashboard accessible
- ✅ Alerts set up for critical errors
- ✅ Documentation complete

---

## 🔧 Quick Reference Commands

### Check backend logs
```bash
az webapp log tail --name suna-backend-app --resource-group <rg>
```

### Test backend locally
```bash
cd apps/backend && uv run uvicorn main:app --reload
```

### Deploy backend
```bash
az webapp deployment source sync --name suna-backend-app --resource-group <rg>
```

### Deploy frontend
```bash
cd apps/frontend && vercel --prod
```

### Check production
```bash
curl https://suna-backend-app.azurewebsites.net/v1/health
curl https://carbonscope.ensimu.space
```

---

## 🆘 Rollback Plan

If deployment fails:

```bash
# Backend rollback
az webapp deployment slot swap \
  --name suna-backend-app \
  --resource-group <rg> \
  --slot staging

# Frontend rollback
vercel rollback
```

---

## 📝 Notes

- **Context:** Live production site with users
- **Risk:** Medium - critical endpoint broken
- **Strategy:** Fix critical issue first, then polish
- **Timeline:** Phases can run in parallel after Phase 1 completes
