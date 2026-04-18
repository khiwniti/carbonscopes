# Roadmap: CarbonScopes

## Overview

Bring the existing CarbonScopes brownfield codebase from its current state to production-ready. Start with critical fixes and security hardening, then establish CI/CD quality gates, then validate the core carbon calculation pipeline end-to-end, and finally stabilize auth and session management.

## Phases

- [x] **Phase 1: Critical Fixes & Security** — Resolve blocking issues preventing safe development
- [ ] **Phase 2: CI/CD & Build Hardening** — Establish quality gates and clean deployment
- [ ] **Phase 3: Core Pipeline Validation** — Verify carbon calculation pipeline end-to-end
- [ ] **Phase 4: Auth & Session Stabilization** — Ensure consistent auth across frontend/backend

## Phase Details

### Phase 1: Critical Fixes & Security
**Goal**: Remove all blocking issues that prevent safe, clean development. Repo should be in a clean state with no merge conflicts, no leaked secrets, and no dead code paths.
**Depends on**: Nothing (first phase)
**Requirements**: FIX-01, FIX-02, FIX-03, FIX-04, SEC-01, SEC-03, ARCH-02, AUTH-01, AUTH-02
**Success Criteria** (what must be TRUE):
1. `playwright.config.ts` has no merge conflict markers and E2E test runner starts cleanly
2. No session/debug HTML files in repo root
3. No secrets committed in tracked files; `.gitignore` properly excludes env files
4. Disabled billing imports removed or properly gated with feature flags
5. CSP headers tightened for production builds
6. Empty `backend/boq/` directory either populated or removed
7. Google and GitHub OAuth flows work (manual verification)
**Plans**: 3 plans

Plans:
- [x] 01-01: Resolve merge conflicts and remove repo debris (FIX-01, FIX-02, ARCH-02)
- [x] 01-02: Security audit — env files, secrets, CSP hardening (FIX-03, SEC-01, SEC-03)
- [x] 01-03: Clean up dead code and verify OAuth auth flows (FIX-04, AUTH-01, AUTH-02)

### Phase 2: CI/CD & Build Hardening
**Goal**: Establish automated quality gates so broken code cannot reach production. Clean deployment configuration.
**Depends on**: Phase 1
**Requirements**: FIX-05, FIX-06, FIX-07, SEC-02
**Success Criteria** (what must be TRUE):
1. GitHub Actions CI runs lint + test on every push
2. CI fails on test failures or lint errors
3. Secret scanning runs in CI pipeline
4. Canonical deployment path documented (single Dockerfile or Cloudflare config)
5. Frontend build succeeds reproducibly (document memory requirements if 4GB still needed)
**Plans**: 2 plans

Plans:
- [ ] 02-01: Add test, lint, and secret scanning to GitHub Actions CI (FIX-06, SEC-02)
- [ ] 02-02: Consolidate deployment config — pick canonical path, remove unused Dockerfiles (FIX-05, FIX-07)

### Phase 3: Core Pipeline Validation
**Goal**: Verify the end-to-end carbon calculation pipeline works correctly from BOQ upload through compliance checking. This is the core value proposition.
**Depends on**: Phase 1
**Requirements**: CARBON-01, CARBON-02, CARBON-03, CARBON-04, CARBON-05, ARCH-01, ARCH-03, DASH-01, DASH-02, DASH-03
**Success Criteria** (what must be TRUE):
1. BOQ file uploads and is parsed by the agent system
2. Materials are matched to TGO database entries via knowledge graph
3. Brightway2 carbon calculation returns deterministic results for known inputs
4. EDGE V3 certification check returns correct PASS/FAIL
5. TREES MR1 compliance check returns correct PASS/FAIL
6. Material alternatives engine suggests valid lower-carbon options
7. Dashboard displays carbon summary data from calculations
8. Carbon reports generate from calculation results
9. Agent pipeline recovers gracefully from individual agent failures
**Plans**: 3 plans

Plans:
- [ ] 03-01: Validate BOQ parsing and material matching pipeline (CARBON-01, CARBON-02)
- [ ] 03-02: Validate carbon calculation, compliance checks, and alternatives (CARBON-03, CARBON-04, CARBON-05)
- [ ] 03-03: Validate dashboard, reporting, and agent error recovery (DASH-01, DASH-02, DASH-03, ARCH-03)

### Phase 4: Auth & Session Stabilization
**Goal**: Ensure authentication is consistent and reliable across the full stack. No session mismatches between frontend and backend.
**Depends on**: Phase 1, Phase 3
**Requirements**: AUTH-03
**Success Criteria** (what must be TRUE):
1. Frontend NextAuth sessions and backend Supabase auth are synchronized
2. Token refresh works without page reload
3. Logout clears sessions on both frontend and backend
4. Protected API routes reject unauthenticated requests correctly
**Plans**: 2 plans

Plans:
- [ ] 04-01: Audit and fix session synchronization between NextAuth and Supabase (AUTH-03)
- [ ] 04-02: Test auth edge cases — token refresh, logout, expired sessions, concurrent tabs
