# CarbonScope Production Fix - Project State

**Created:** 2026-04-06
**Status:** ACTIVE - Production error remediation
**Live Site:** https://carbonscope.ensimu.space
**Backend:** https://suna-backend-app.azurewebsites.net

## Current Milestone

**M1: Production Stability** - Fix all production errors and establish monitoring

## Active Phases

- Phase 1: Critical Error Fix (Backend /v1/agents 500)
- Phase 2: Low Priority Cleanup (GitHub stars 404)
- Phase 3: Monitoring & Prevention

## Known Issues

### 🔴 CRITICAL (P0)
- Backend `/v1/agents` returns HTTP 500 - BLOCKS ALL USERS
- Location: `apps/backend/routers/v1/agents.py` (expected)
- Impact: Users cannot list agents, cannot start projects
- Root cause: Unknown - needs backend logs

### 🟡 LOW (P3)
- GitHub stars API returns 404 from CarbonScope-ai/suna
- Location: `apps/frontend/src/hooks/utils/use-github-stars.ts`
- Impact: Console pollution only, no functional impact

## Architecture

**Frontend:** Next.js 15 (App Router) + React 19 + Tailwind
**Backend:** Python + FastAPI + Prisma
**Database:** Supabase (PostgreSQL)
**Cache:** Redis
**Hosting:** Vercel (frontend) + Azure App Service (backend)

## Next Actions

1. Get Azure backend logs to identify 500 error root cause
2. Fix critical /v1/agents endpoint
3. Clean up GitHub stars console warnings
4. Add production monitoring
