# Codebase Structure

**Analysis Date:** 2026-04-06

## Directory Layout

```
carbonscopes/
├── apps/                       # Multi-platform applications
│   ├── frontend/               # Next.js web application
│   ├── desktop/                # Electron desktop app
│   ├── mobile/                 # React Native mobile app
│   └── auth.disabled.backup/   # Legacy auth module
├── backend/                    # FastAPI Python backend
│   ├── core/                   # Business domain modules
│   ├── agents/                 # Specialized agent implementations
│   ├── auth/                   # Authentication logic
│   ├── supabase/               # Database integration
│   ├── api.py                  # Main application entry
│   └── tests/                  # Backend test suite
├── packages/                   # Shared workspace packages
│   └── shared/                 # @agentpress/shared package
├── sdk/                        # Client SDKs and libraries
├── infra/                      # Infrastructure as code
├── scripts/                    # Automation and utility scripts
├── setup/                      # Setup and initialization scripts
├── supabase/                   # Supabase project configuration
├── docs/                       # Documentation
├── .planning/                  # GSD planning documents
│   └── codebase/               # Architecture documentation
├── docker-compose.yaml         # Local development orchestration
├── package.json                # Monorepo workspace configuration
├── pnpm-workspace.yaml         # pnpm workspace definition
└── pyproject.toml              # Python project configuration
```

## Directory Purposes

**apps/frontend/**
- Purpose: Next.js 15 web application with App Router
- Contains: Pages, components, hooks, stores, API routes
- Key files: `src/app/layout.tsx`, `next.config.ts`, `package.json`
- Build output: `.next/` standalone bundle
- Deployment: Azure Web Apps, Vercel, Docker container

**apps/desktop/**
- Purpose: Electron desktop application wrapping frontend
- Contains: Main process, renderer process, native integrations
- Platform: macOS, Windows, Linux
- Distribution: Native installers and app bundles

**apps/mobile/**
- Purpose: React Native mobile application
- Contains: Native screens, shared components, platform-specific code
- Platform: iOS, Android
- Distribution: App Store, Google Play

**backend/**
- Purpose: FastAPI Python API server
- Contains: REST endpoints, business logic, database operations
- Entry: `api.py` with FastAPI app initialization
- Structure: Domain-driven modular organization
- Deployment: Azure App Service, Docker containers

**backend/core/**
- Purpose: Core business domain modules
- Modules: `agents/`, `agentpress/`, `threads/`, `carbon/`, `billing/`, `endpoints/`
- Pattern: Each module has `api.py` (routes), `repo.py` (data access), service files
- Organization: Feature-based vertical slices

**backend/core/agentpress/**
- Purpose: Agent orchestration framework
- Contains: Thread manager, tool registry, processor config, MCP integration
- Key abstraction: `ThreadManager` for conversation lifecycle
- Subdirectories: `thread_manager/`, `example/`

**backend/core/agents/**
- Purpose: Specialized agent implementations
- Contains: BOQ parser, carbon calculator, compliance, cost analyst, material analyst
- Pattern: Each agent extends base agent class with domain-specific tools
- Configuration: Agent config files with model and tool specifications

**backend/core/endpoints/**
- Purpose: API endpoint handlers grouped by feature
- Contains: Account management, file uploads, carbon, BOQ, tools, system status
- Pattern: Router + repository pattern
- Files: `*_api.py` for routes, `*_repo.py` for data access

**backend/core/services/**
- Purpose: Shared infrastructure services
- Contains: Supabase client, Redis, LLM, email, Langfuse, transcription
- Pattern: Singleton connections with configuration management
- Key files: `supabase.py`, `redis.py`, `llm.py`, `langfuse.py`

**backend/auth/**
- Purpose: Authentication and authorization logic
- Contains: JWT validation, Supabase auth integration, rate limiting
- Key file: `api.py` with auth endpoints

**backend/supabase/**
- Purpose: Database utilities and migrations
- Contains: Database helpers, connection management
- Integration: Works with Supabase PostgreSQL instance

**backend/tests/**
- Purpose: Backend test suite
- Contains: Unit tests, integration tests, fixtures
- Framework: pytest with async support
- Configuration: `pytest.ini`, `conftest.py`

**apps/frontend/src/app/**
- Purpose: Next.js App Router pages and layouts
- Contains: Route groups, dynamic routes, API routes
- Route Groups: `(dashboard)/`, `(home)/`, `(public)/`
- Special files: `layout.tsx`, `page.tsx`, `error.tsx`, `not-found.tsx`

**apps/frontend/src/app/(dashboard)/**
- Purpose: Authenticated dashboard routes
- Routes: `/dashboard`, `/projects`, `/thread`, `/settings`, `/agents`, `/admin`
- Layout: `layout.tsx` with `DashboardLayoutContent` wrapper
- Pattern: Shared dashboard navigation and auth check

**apps/frontend/src/app/(home)/**
- Purpose: Public marketing and informational pages
- Routes: `/`, `/about`, `/pricing`, `/tutorials`, `/careers`
- Layout: Marketing-focused with different navigation
- Pattern: Public access, SEO optimized

**apps/frontend/src/app/api/**
- Purpose: Next.js API routes (backend-for-frontend)
- Routes: `/api/health`, `/api/share-page`, `/api/triggers`, `/api/v1/*`
- Pattern: Proxy routes to backend or edge functions
- Usage: OAuth callbacks, webhooks, image processing

**apps/frontend/src/components/**
- Purpose: Reusable React components
- Organization: Feature-based folders (agents, dashboard, auth, billing, etc.)
- Pattern: Component + hooks + types co-located
- Special: `ui/` for shadcn/ui primitives
- Key files: `AuthProvider.tsx`, `ClientProvidersWrapper.tsx`, `ProvidersClient.tsx`

**apps/frontend/src/lib/**
- Purpose: Utilities, clients, and configuration
- Contains: API client, Supabase client, auth utilities, constants
- Key files: `api-client.ts`, `supabase/`, `auth.ts.disabled`, `config.ts`
- Subdirectories: `api/`, `constants/`, `icons/`, `analytics/`

**apps/frontend/src/stores/**
- Purpose: Client-side state management with Zustand
- Contains: Thread navigation, model selection, subscription, UI state
- Pattern: One store per feature with selector hooks
- Example: `thread-navigation-store.ts`, `model-store.ts`, `subscription-store.tsx`

**apps/frontend/src/hooks/**
- Purpose: Reusable React hooks
- Contains: Custom hooks for data fetching, UI interactions, utilities
- Pattern: `use*` naming convention
- Organization: Co-located with related features or in root hooks/

**packages/shared/**
- Purpose: Shared code across frontend platforms (web/desktop/mobile)
- Contains: Common types, utilities, business logic
- Usage: `@agentpress/shared` workspace package
- Import: `import { ... } from '@agentpress/shared'`

**sdk/**
- Purpose: Client SDKs for external consumers
- Contains: API client libraries, type definitions
- Distribution: Published to npm or distributed as source

**infra/**
- Purpose: Infrastructure as code and deployment configurations
- Contains: Terraform, ARM templates, deployment scripts
- Target: Azure resources, networking, monitoring

**scripts/**
- Purpose: Automation and utility scripts
- Contains: Deployment scripts, migration tools, data processing
- Usage: Invoked manually or via CI/CD pipelines

**setup/**
- Purpose: Initial setup and onboarding scripts
- Contains: Environment setup, dependency installation, configuration
- Usage: New developer onboarding, environment initialization

**supabase/**
- Purpose: Supabase project configuration
- Contains: Migrations, seed data, RLS policies
- Structure: Standard Supabase CLI project layout

**.planning/codebase/**
- Purpose: GSD framework documentation
- Contains: Architecture, structure, conventions, testing, concerns
- Pattern: Markdown documents for different analysis aspects
- Usage: Reference for AI-assisted development and planning

## Key File Locations

**Entry Points:**
- Frontend: `apps/frontend/src/app/layout.tsx`
- Backend: `backend/api.py`
- Desktop: `apps/desktop/src/main/index.ts` (assumed)
- Mobile: `apps/mobile/index.js` (assumed)

**Configuration:**
- Next.js: `apps/frontend/next.config.ts`
- FastAPI: `backend/api.py` (app configuration)
- Python deps: `backend/pyproject.toml`
- Node deps: `package.json`, `pnpm-lock.yaml`
- Environment: `.env.example`, `.env.local`, `.env.production`

**Core Logic:**
- Thread management: `backend/core/agentpress/thread_manager/manager.py`
- API client: `apps/frontend/src/lib/api-client.ts`
- Database: `backend/core/services/supabase.py`
- Auth: `backend/auth/api.py`, `apps/frontend/src/components/AuthProvider.tsx`

**Testing:**
- Frontend E2E: `apps/frontend/e2e/`
- Backend tests: `backend/tests/`
- Test configs: `apps/frontend/playwright.config.ts`, `backend/pytest.ini`

**Documentation:**
- Architecture: `.planning/codebase/ARCHITECTURE.md`
- API docs: `backend/core/*/README.md` (various modules)
- User docs: `docs/` (if present)

## Naming Conventions

**Files:**
- React components: `PascalCase.tsx` (e.g., `AuthProvider.tsx`)
- Utility modules: `kebab-case.ts` (e.g., `api-client.ts`)
- Python modules: `snake_case.py` (e.g., `thread_manager.py`)
- Config files: lowercase with dots (e.g., `next.config.ts`)

**Directories:**
- Features: `lowercase` or `kebab-case` (e.g., `agents`, `file-editors`)
- Route groups: `(group-name)` with parentheses (e.g., `(dashboard)`)
- Private modules: `_prefix` for Next.js private folders (e.g., `__tests__`)

**Components:**
- UI primitives: lowercase (e.g., `button`, `dialog`)
- Feature components: PascalCase (e.g., `ThreadChat`, `AgentSelector`)
- Layout components: suffix with `Layout` or `Wrapper`

## Where to Add New Code

**New Feature:**
- Frontend primary code: `apps/frontend/src/components/{feature}/`
- Backend logic: `backend/core/{feature}/`
- API endpoints: `backend/core/{feature}/api.py`
- Database repo: `backend/core/{feature}/repo.py`
- Frontend stores: `apps/frontend/src/stores/{feature}-store.ts`
- Tests: `backend/tests/{feature}/` and `apps/frontend/e2e/{feature}.spec.ts`

**New Page:**
- Public page: `apps/frontend/src/app/(home)/{page}/page.tsx`
- Dashboard page: `apps/frontend/src/app/(dashboard)/{page}/page.tsx`
- API route: `apps/frontend/src/app/api/{route}/route.ts`

**New Component:**
- Reusable UI: `apps/frontend/src/components/ui/{component}.tsx`
- Feature-specific: `apps/frontend/src/components/{feature}/{component}.tsx`
- Shared across platforms: `packages/shared/src/components/{component}.tsx`

**New Agent:**
- Implementation: `backend/core/agents/{agent_name}_agent.py`
- Config: `backend/core/agents/config.py` (add configuration)
- Tools: `backend/core/agents/{agent_name}_tools.py` (if custom tools needed)
- Tests: `backend/tests/agents/test_{agent_name}_agent.py`

**Utilities:**
- Frontend helpers: `apps/frontend/src/lib/{utility}.ts`
- Backend helpers: `backend/core/utils/{utility}.py`
- Shared utilities: `packages/shared/src/utils/{utility}.ts`

**New API Endpoint:**
- Router: `backend/core/endpoints/{feature}_api.py`
- Repository: `backend/core/endpoints/{feature}_repo.py`
- Register in: `backend/api.py` (add router import and include)

## Special Directories

**.next/**
- Purpose: Next.js build output
- Generated: Yes (on `next build`)
- Committed: No (.gitignored)
- Contains: Compiled pages, static assets, server bundles

**node_modules/**
- Purpose: Node.js dependencies
- Generated: Yes (on `pnpm install`)
- Committed: No (.gitignored)
- Managed by: pnpm with `pnpm-lock.yaml`

**.planning/**
- Purpose: GSD framework planning documents
- Generated: Partially (by GSD commands)
- Committed: Yes (project knowledge)
- Pattern: Markdown documentation for AI-assisted development

**e2e-screenshots/**
- Purpose: Playwright test screenshots
- Generated: Yes (on test failures or explicit captures)
- Committed: No (typically .gitignored)
- Usage: Visual regression testing, debugging

**__pycache__/**
- Purpose: Python bytecode cache
- Generated: Yes (on Python import)
- Committed: No (.gitignored)
- Management: Automatically managed by Python interpreter

**prisma/** (if present)
- Purpose: Database schema and migrations
- Generated: Migrations generated via Prisma CLI
- Committed: Schema and migrations committed, generated client ignored
- Usage: Database versioning and type safety

---

*Structure analysis: 2026-04-06*
