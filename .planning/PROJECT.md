---
code: CS
title: CarbonScopes
status: active
version: 1.0
date: 2026-04-18
---

# CarbonScopes

Comprehensive carbon accounting platform for tracking, analyzing, and managing carbon footprints for businesses and individuals. Specialized in construction industry LCA (Life Cycle Assessment) with AI-powered multi-agent analysis.

## What This Is

CarbonScopes is an AI-driven carbon accounting SaaS that lets users:
1. Upload Bill of Quantities (BOQ) documents for construction projects
2. Automatically parse and categorize materials using AI agents
3. Calculate embodied carbon using Brightway2 LCA engine with deterministic calculations
4. Check compliance against EDGE V3 and TREES MR1 green building certifications
5. Explore material alternatives for carbon reduction
6. Generate carbon reports and scenario analyses

## Core Value

**Accurate, automated embodied carbon calculation from BOQ data** -- upload a BOQ, get certified carbon results. Everything else supports this loop.

## Context

- **Domain**: Construction industry carbon accounting / LCA
- **Users**: Sustainability consultants, architects, construction firms, green building certifiers
- **Stage**: Brownfield -- extensive existing codebase with backend + frontend
- **Team**: Solo developer + AI agents
- **Stack**: Python/FastAPI backend, Next.js 15 frontend, Supabase DB, Brightway2 LCA

## Tech Stack

- **Backend**: Python 3.11+ / FastAPI 0.115.12 / Uvicorn / Gunicorn
- **AI**: LiteLLM (multi-model), OpenAI, LangFuse (observability), MCP 1.9.4
- **LCA Engine**: Brightway2 with custom deterministic carbon calculator
- **Knowledge Graph**: RDFLib / SPARQL (TGO material database)
- **Database**: Supabase (PostgreSQL) + Prisma ORM + Redis/Upstash
- **Frontend**: Next.js 15 / React 19 / TypeScript / Tailwind CSS / shadcn-ui
- **State**: Zustand (client) + TanStack React Query (server)
- **Auth**: NextAuth.js (Google/GitHub OAuth) + Supabase Auth + PyJWT
- **Payments**: Stripe (currently disabled)
- **Integrations**: Composio, E2B sandbox, Daytona, Tavily, Exa
- **Deployment**: Cloudflare Workers (primary) / Docker / Vercel (alternate)
- **CI/CD**: GitHub Actions (build + deploy only, no test/lint gate)

## Architecture

- **Multi-agent AI system**: Supervisor routes to 12+ specialized agents (carbon calculator, material analyst, compliance checker, BOQ parser, etc.)
- **AgentPress**: Custom LLM orchestration framework (thread manager, tool registry, context manager, prompt caching)
- **LCA pipeline**: BOQ upload → parse → material match → Brightway2 calculation → compliance check → report
- **Monorepo**: pnpm workspaces (apps/frontend + packages/shared), backend is separate Python package
- **API pattern**: Domain modules with api.py / service.py / repo.py under `backend/core/`

## Requirements

### Validated

- ✓ User authentication (Google, GitHub, email/password) — existing
- ✓ BOQ document upload and parsing — existing
- ✓ Multi-agent AI chat interface — existing
- ✓ Carbon calculation via Brightway2 — existing
- ✓ TGO material database with knowledge graph — existing
- ✓ EDGE V3 / TREES MR1 compliance checking — existing
- ✓ Dashboard with project management — existing
- ✓ Stripe billing integration (disabled but functional) — existing
- ✓ Admin panel with analytics — existing
- ✓ Knowledge base with document ingestion — existing
- ✓ Real-time chat with streaming responses — existing
- ✓ File upload/management — existing
- ✓ Notification system (Novu) — existing
- ✓ E2E test infrastructure (Playwright) — existing

### Active

- [ ] Fix merge conflict in playwright.config.ts
- [ ] Remove session HTML file from repo root
- [ ] Verify .env.production is not committed with secrets
- [ ] Clean up disabled billing imports (dead code)
- [ ] Consolidate Dockerfiles to canonical deployment path
- [ ] Add test + lint steps to CI pipeline
- [ ] Reduce frontend build memory requirement (currently 4GB heap)
- [ ] Establish single source of truth for DB schema (Prisma vs Supabase)

### Out of Scope

- Mobile app — no current mobile implementation despite pnpm script reference
- GraphDB production deployment — current in-memory RDFLib is sufficient for MVP
- Voice API (VAPI) integration — config exists but not core value
- Apify web scraping — peripheral feature

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Cloudflare Workers as primary deploy | Edge performance, low cost | In progress (8 Dockerfiles suggest uncertainty) |
| Brightway2 for LCA calculations | Industry standard, deterministic | Working |
| Multi-agent architecture | Specialized agents > monolithic | Working, complex |
| Supabase + Prisma dual ORM | Historical evolution | Needs consolidation |
| AgentPress custom framework | Flexibility over LangChain | Working |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-18 after codebase mapping and project initialization*
