---
project: CS
version: 1.0
updated: 2026-04-18
---

# CarbonScopes State

## Current Phase: Production Readiness Audit & Fix

### Active Issues (from codebase/CONCERNS.md)
| ID | Severity | Status | Description |
|----|----------|--------|-------------|
| F-01 | HIGH | pending | Merge conflict in playwright.config.ts |
| F-02 | HIGH | pending | Session HTML file in repo root |
| F-03 | HIGH | pending | .env.production may contain secrets |
| F-04 | MEDIUM | pending | Disabled billing imports (dead code) |
| F-05 | MEDIUM | pending | 8 Dockerfiles (unclear canonical path) |
| F-06 | HIGH | pending | No test/lint in CI pipeline |
| F-07 | HIGH | pending | Production build verification |
| F-08 | MEDIUM | pending | 4GB heap required for build |
| F-09 | MEDIUM | pending | Mixed ORM (Prisma + Supabase) — no schema source of truth |
| F-10 | LOW | pending | Empty BOQ module directory |
| F-11 | MEDIUM | pending | Broad CSP connect-src in dev mode |

## Quick Tasks Completed
| Date | Task | Status |
|------|------|--------|
| 2026-04-18 | Codebase mapping (7 docs) | ✓ complete |
| 2026-04-18 | PROJECT.md initialization | ✓ complete |
| 2026-04-18 | GSD config.json created | ✓ complete |

## Codebase Map
- Location: `.planning/codebase/`
- Documents: STACK.md, ARCHITECTURE.md, STRUCTURE.md, CONVENTIONS.md, TESTING.md, INTEGRATIONS.md, CONCERNS.md
- Total: 868 lines

## Next Steps
1. Define requirements (REQUIREMENTS.md) from brownfield analysis
2. Create roadmap (ROADMAP.md) for production readiness
3. Execute Phase 1: Fix critical issues (F-01 through F-07)
