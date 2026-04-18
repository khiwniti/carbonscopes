# Requirements: CarbonScopes

**Defined:** 2026-04-18
**Core Value:** Accurate, automated embodied carbon calculation from BOQ data

## v1 Requirements (Production Readiness)

Requirements to bring existing brownfield codebase to production-ready state. Each maps to roadmap phases.

### Critical Fixes

- [ ] **FIX-01**: Merge conflict in `playwright.config.ts` is resolved and E2E tests run cleanly
- [ ] **FIX-02**: Session/debug HTML file removed from repo root
- [ ] **FIX-03**: `.env.production` verified not committed with secrets; `.gitignore` covers all env files
- [ ] **FIX-04**: Disabled billing router imports cleaned up (remove or properly gate dead code)
- [ ] **FIX-05**: Canonical deployment path established (reduce from 8 Dockerfiles)
- [ ] **FIX-06**: CI pipeline includes test + lint steps (not just build + deploy)
- [ ] **FIX-07**: Frontend production build succeeds without 4GB heap override (or documented as required)

### Security

- [ ] **SEC-01**: CSP connect-src tightened for production (remove broad localhost allowlist)
- [ ] **SEC-02**: Secret scanning added to CI pipeline
- [ ] **SEC-03**: All API keys in codebase use environment variables (no hardcoded values)

### Architecture

- [ ] **ARCH-01**: Single source of truth for database schema (consolidate Prisma + Supabase)
- [ ] **ARCH-02**: Empty `backend/boq/` directory removed or populated (consistent module organization)
- [ ] **ARCH-03**: Agent system has error recovery (agent failures don't crash the pipeline)

### Carbon Calculation Core

- [ ] **CARBON-01**: BOQ upload → material parsing → carbon calculation pipeline works end-to-end
- [ ] **CARBON-02**: TGO material database loads correctly into knowledge graph
- [ ] **CARBON-03**: EDGE V3 certification check returns accurate PASS/FAIL
- [ ] **CARBON-04**: TREES MR1 compliance check returns accurate PASS/FAIL
- [ ] **CARBON-05**: Material alternatives engine suggests valid lower-carbon options

### Dashboard & Reporting

- [ ] **DASH-01**: Dashboard loads with project list and carbon summary data
- [ ] **DASH-02**: Carbon reports generate correctly from calculation results
- [ ] **DASH-03**: File upload and management works for BOQ documents

### Authentication

- [ ] **AUTH-01**: Google OAuth login works end-to-end
- [ ] **AUTH-02**: GitHub OAuth login works end-to-end
- [ ] **AUTH-03**: Session management consistent between NextAuth (frontend) and Supabase (backend)

## v2 Requirements (Feature Enhancements)

Deferred to future release.

### User Experience

- **UX-01**: Onboarding flow for new users (guided BOQ upload)
- **UX-02**: Material alternative comparison view
- **UX-03**: Scenario analysis with side-by-side comparison

### Platform

- **PLAT-01**: Billing re-enabled with proper Stripe integration
- **PLAT-02**: Team/workspace support for multi-user projects
- **PLAT-03**: API documentation (OpenAPI/Swagger) publicly accessible
- **PLAT-04**: Mobile-responsive dashboard

### Integrations

- **INT-01**: Export carbon reports to PDF (WeasyPrint pipeline working)
- **INT-02**: Composio integrations functional and documented
- **INT-03**: MCP server provides carbon calculation tools to external AI agents

## Out of Scope

| Feature | Reason |
|---------|--------|
| Mobile app (React Native) | No current implementation; web-first |
| GraphDB production deployment | In-memory RDFLib sufficient for MVP |
| Voice API (VAPI) | Config exists but not core value proposition |
| Apify web scraping | Peripheral, not needed for carbon calc |
| E2B code interpreter in prod | Sandbox feature, not core |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FIX-01 | Phase 1 | Pending |
| FIX-02 | Phase 1 | Pending |
| FIX-03 | Phase 1 | Pending |
| FIX-04 | Phase 1 | Pending |
| FIX-05 | Phase 2 | Pending |
| FIX-06 | Phase 2 | Pending |
| FIX-07 | Phase 2 | Pending |
| SEC-01 | Phase 1 | Pending |
| SEC-02 | Phase 2 | Pending |
| SEC-03 | Phase 1 | Pending |
| ARCH-01 | Phase 3 | Pending |
| ARCH-02 | Phase 1 | Pending |
| ARCH-03 | Phase 3 | Pending |
| CARBON-01 | Phase 3 | Pending |
| CARBON-02 | Phase 3 | Pending |
| CARBON-03 | Phase 3 | Pending |
| CARBON-04 | Phase 3 | Pending |
| CARBON-05 | Phase 3 | Pending |
| DASH-01 | Phase 3 | Pending |
| DASH-02 | Phase 3 | Pending |
| DASH-03 | Phase 3 | Pending |
| AUTH-01 | Phase 1 | Pending |
| AUTH-02 | Phase 1 | Pending |
| AUTH-03 | Phase 4 | Pending |

**Coverage:**
- v1 requirements: 23 total
- Mapped to phases: 23
- Unmapped: 0

---
*Requirements defined: 2026-04-18*
*Last updated: 2026-04-18 after codebase mapping*
