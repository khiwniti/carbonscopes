# CarbonScopes Conventions

> Mapped: 2026-04-18

## Backend Conventions

### Python Style
- **Python 3.11+** required (`requires-python = ">=3.11"`)
- Type hints used throughout (`typing.Dict`, `typing.Any`, `typing.List`)
- Pydantic models for API request/response schemas (`backend/core/api_models/`)
- Module docstrings on key files (e.g., carbon API, agents)
- Standard Python logging (`logging.getLogger(__name__)`)

### Project Structure Convention
- **Domain-driven modules**: Each feature domain lives in its own directory under `backend/core/`
- **Module pattern**: Each domain module typically contains:
  - `api.py` — FastAPI router with endpoints
  - `service.py` — Business logic
  - `repo.py` — Database/repository layer (where needed)
  - `__init__.py` — Module exports
  - `models.py` — Pydantic/DB models (where needed)
  - `background_jobs.py` — Async tasks (where needed)

### API Conventions
- **FastAPI routers**: Each module exposes an `APIRouter` imported and registered in `backend/api.py`
- **Router prefix pattern**: `/v1/{domain}` (e.g., `/v1/carbon/calculate`, `/v1/tgo/load`)
- **Router tagging**: Routers use `tags=["domain"]` for OpenAPI grouping
- **Pydantic models**: Request/response bodies defined with `BaseModel`
- **Error handling**: `HTTPException` raised with appropriate status codes

### Agent Conventions
- **Base class**: All agents extend `Agent` from `backend/core/agents/base.py`
- **State pattern**: `AgentState` used for inter-agent communication
- **Capabilities declaration**: Each agent defines capabilities in docstring (e.g., `calculate:carbon`)
- **Supervisor pattern**: `supervisor.py` routes tasks to specialized agents
- **Agent registry**: Agents registered via `agent_loader.py`, `agent_crud.py`

### Configuration
- **Environment-based**: Config loaded from `.env` files via `python-dotenv`
- **Centralized configs**: `backend/core/config/` holds domain-specific config modules
- **Supabase env vars**: `DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_KEY`

## Frontend Conventions

### TypeScript/React Style
- **React 19** with hooks-first approach (no class components)
- **TypeScript strict mode** enabled
- **App Router** (Next.js 15) — no Pages Router
- **Server/Client component split**: Server components by default, `"use client"` directive where needed

### File Naming
- **Components**: PascalCase `.tsx` files (e.g., `DashboardWidget.tsx`)
- **Hooks**: camelCase `.ts` files in `hooks/` directory (e.g., `useThreads.ts`)
- **API routes**: `route.ts` in App Router convention
- **Types**: `types/` directory with domain-specific type files
- **Constants**: `lib/constants/` directory

### Component Organization
- **shadcn/ui pattern**: UI primitives in `components/ui/`, composed in feature components
- **Feature-based grouping**: Components organized by domain (thread, agents, dashboard, etc.)
- **Barrel exports**: Likely via index files in component directories

### State Management Pattern
- **Server state**: TanStack React Query for API data fetching/caching
- **Client state**: Zustand stores in `src/stores/`
- **Form state**: React Hook Form + Zod resolvers (`@hookform/resolvers`)

### Styling
- **Tailwind CSS** — utility-first approach
- **PostCSS** with MJS config (`postcss.config.mjs`)
- **shadcn/ui theming**: `components.json` configuration

### Internationalization
- **FormatJS** libraries (`@formatjs/fast-memoize`, `@formatjs/icu-messageformat-parser`)
- **Translation files**: `apps/frontend/translations/`

## Monorepo Conventions

### Package Manager
- **pnpm** with workspaces
- Root `package.json` defines workspace scripts
- `pnpm-lock.yaml` at root

### Workspace Structure
- `apps/frontend` — Next.js application (`carbonscope-frontend`)
- `packages/shared` — Shared library (`@agentpress/shared`)
- Backend is NOT a pnpm workspace (Python, managed separately)

### Import Conventions
- Shared package imports: `@agentpress/shared`, `@agentpress/shared/types`, etc.
- Relative imports within apps

## Error Handling Patterns
- **Backend**: `HTTPException` in FastAPI, `structlog` for structured error logging
- **Frontend**: React Query error boundaries, error handler tests in `__tests__/error-handler.test.ts`
- **API boundary**: Backend returns standard HTTP error codes, frontend handles via React Query mutations/queries

## Security Patterns
- **CSP headers**: Comprehensive Content-Security-Policy in `next.config.ts`
- **CORS**: Configured in FastAPI middleware (`backend/api.py`)
- **Rate limiting**: `backend/core/middleware/rate_limit.py` via Redis
- **Auth**: JWT-based with Supabase, NextAuth.js for OAuth
- **Input sanitization**: Tests in `__tests__/sanitize.test.ts`
