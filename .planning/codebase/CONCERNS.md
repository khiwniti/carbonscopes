# CarbonScopes Technical Concerns

> Mapped: 2026-04-18

## Critical Issues

### 1. Git Merge Conflict in Config
- **File**: `apps/frontend/playwright.config.ts`
- **Issue**: Unresolved merge conflict markers present (`<<<<<<< HEAD`, `=======`)
- **Impact**: Playwright config is broken — E2E tests cannot run until resolved
- **Fix**: Resolve the webServer configuration conflict

### 2. Heavy Dependency Surface
- **Backend**: 60+ Python dependencies including niche/unstable packages (vncdotool, python-ripgrep, vtracer)
- **Frontend**: 100+ npm dependencies with many Radix UI primitives imported individually
- **Risk**: Supply chain vulnerability, maintenance burden, potential version conflicts
- **Example**: `python-ripgrep==0.0.6` is a very low-version package

### 3. Mixed ORM Strategy
- **Issue**: Backend uses both Prisma (Python client 0.15.0) and Supabase client for DB access
- **Also**: Prisma schema lives in `apps/frontend/prisma/` not in backend
- **Risk**: Schema drift between frontend Prisma and backend access patterns
- **Impact**: No single source of truth for database schema

## Technical Debt

### 4. Incomplete BOQ Module
- **Location**: `backend/boq/` directory exists but is empty
- **Issue**: BOQ (Bill of Quantities) parsing logic is in `backend/core/agents/boq_parser_agent.py` and `backend/agents/` instead
- **Impact**: Confusing module organization — code doesn't match directory structure

### 5. Empty/Stub Modules
- Several modules appear to have minimal implementation:
  - `backend/boq/` — empty
  - `backend/core/jit/` — purpose unclear
  - `backend/core/google/` — may be unused
- **Risk**: Dead code accumulation

### 6. Dual Deployment Configuration
- **Cloudflare**: `wrangler.toml`, `cloudflare-build.sh`, dedicated Dockerfile and CI workflow
- **Vercel**: `vercel.json` present
- **8 Dockerfiles**: `Dockerfile`, `Dockerfile.build`, `Dockerfile.production`, `Dockerfile.runtime`, `Dockerfile.minimal`, `Dockerfile.standalone`, `Dockerfile.prebuilt`, `Dockerfile.simple`
- **Risk**: Configuration drift, unclear which is the canonical deployment path

### 7. Billing Disabled but Present
- **Evidence**: `# BILLING DISABLED` comments in `backend/api.py` but billing router still imported
- **Impact**: Dead code paths, potential security surface from unused payment endpoints

## Security Concerns

### 8. Session File in Repository
- **File**: `pi-session-2026-04-06T16-50-21-142Z_c2f81c38-0162-4fb6-bc84-6ed6aecbf087.html`
- **Issue**: What appears to be a session/debug HTML file committed to root directory
- **Risk**: May contain sensitive session data or debug information

### 9. Environment Variable Exposure
- **Template file**: `.env.local.template` contains placeholder secrets
- **Risk**: `.env.production` file exists in frontend directory — should not be committed
- **Note**: `.gitignore` coverage for `.env*` files should be verified

### 10. Broad CSP Connect-Sources
- **File**: `apps/frontend/next.config.ts`
- **Issue**: `connect-src` allows `http://local-backend http://localhost:*` which is permissive
- **Risk**: In development mode, broad localhost access could be exploited

## Performance Concerns

### 11. Large Frontend Bundle
- **100+ dependencies** in frontend package.json
- **74 UI components** imported from shadcn/ui (many may be tree-shaken, but risk exists)
- **React 19 + compiler disabled**: `reactCompiler: false` in next.config.ts
- **Impact**: Slow initial page load, large JavaScript bundle

### 12. Backend Agent Orchestration Overhead
- Multi-agent system with supervisor routing adds latency
- LLM calls through LiteLLM may have cold-start delays
- Brightway2 LCA calculations can be compute-intensive
- **Mitigation**: Redis caching, prompt caching, rate limiting present

### 13. Memory Build Option
- **Config**: `NODE_OPTIONS='--max-old-space-size=4096'` required for build
- **Issue**: Frontend build requires 4GB heap — indicates large bundle or memory-inefficient build
- **Impact**: CI/CD resource requirements, slow builds

## Fragile Areas

### 14. GraphDB / Knowledge Graph
- **Dual mode**: In-memory RDFLib graph with optional GraphDB
- **Risk**: Behavior differs significantly between modes; tests may pass in-memory but fail with real GraphDB
- **TGO Loading**: File upload-based material loading (`/v1/tgo/load`) with temp file storage

### 15. Agent System Complexity
- 12+ specialized agents with supervisor routing
- Agent state management via `AgentState` pattern
- Checkpointer for agent persistence
- **Risk**: Agent coordination bugs, state inconsistencies, hard-to-debug multi-agent flows

### 16. Authentication Multi-Path
- NextAuth.js (frontend OAuth) + Supabase Auth (backend) + PyJWT
- Multiple auth paths: Google OAuth, GitHub OAuth, phone verification, password reset
- **Risk**: Auth state inconsistencies between frontend and backend sessions

## Missing Infrastructure

### 17. No CI Test Step
- GitHub Actions workflow only builds and deploys
- No automated test execution in CI pipeline
- **Impact**: Broken tests can reach production

### 18. No Linting in CI
- No lint step in GitHub Actions workflow
- Backend linting: `ruff_cache` exists but not integrated in CI
- Frontend: `pnpm lint` available but not in CI
