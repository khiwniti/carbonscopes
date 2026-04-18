# Phase 1: Critical Fixes & Security - Context

**Gathered:** 2026-04-18
**Status:** Ready for planning
**Source:** Codebase mapping + CONCERNS.md analysis

<domain>
## Phase Boundary

Remove all blocking issues that prevent safe, clean development. The repo must be in a clean state with no merge conflicts, no leaked secrets, no dead code paths, and hardened CSP headers. OAuth flows must be verifiable.

**Requirements:** FIX-01, FIX-02, FIX-03, FIX-04, SEC-01, SEC-03, ARCH-02, AUTH-01, AUTH-02

**Codebase context:**
- Codebase map at `.planning/codebase/` (7 documents, 868 lines)
- Key concerns documented in `.planning/codebase/CONCERNS.md`
- Playwright config has unresolved merge conflict markers (`<<<<<<< HEAD`, `=======`)
- Session HTML file at repo root: `pi-session-2026-04-06T16-50-21-142Z_c2f81c38-0162-4fb6-bc84-6ed6aecbf087.html`
- `.env.production` exists in `apps/frontend/` -- needs audit
- Billing imports disabled with comments but still imported in `backend/api.py`
- CSP `connect-src` includes `http://local-backend http://localhost:*` in production
- Empty `backend/boq/` directory
- Auth uses NextAuth.js (Google/GitHub OAuth) + Supabase Auth

</domain>

<decisions>
## Implementation Decisions

### Merge Conflicts & Debris
- Resolve playwright.config.ts by keeping the `reuseExistingServer: true` version (more flexible for dev and CI)
- Delete the session HTML file from repo root entirely
- Remove empty `backend/boq/` directory (BOQ logic lives in `backend/core/agents/` and `backend/agents/`)

### Security
- Audit `.env.production` for hardcoded secrets; if contains any, move to env vars
- Ensure `.gitignore` covers `*.env`, `.env.*`, `!.env.example`, `!.env.template`
- CSP: Remove `http://local-backend http://localhost:*` from production connect-src; keep only in dev condition
- Scan entire repo for hardcoded API keys, tokens, credentials

### Dead Code
- Comment out or remove the billing router import in `backend/api.py` (lines 39-40, 44-45)
- Remove the `# BILLING DISABLED` comments -- just remove the imports entirely
- Keep billing module code in place for future re-enablement

### Auth Verification
- Verify Google OAuth callback URL is configured
- Verify GitHub OAuth callback URL is configured
- Check that NEXTAUTH_SECRET and NEXTAUTH_URL are properly set in env
- Document the auth flow for manual verification

### Claude's Discretion
- Exact resolution strategy for playwright.config.ts merge conflict
- Whether to add `--reporter` flag for better CI test output
- How to handle any additional secrets found during scan
- Whether to add pre-commit hooks for secret detection

</decisions>
