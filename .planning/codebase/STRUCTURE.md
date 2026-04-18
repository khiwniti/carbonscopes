# CarbonScopes Project Structure

> Mapped: 2026-04-18

## Root Directory Layout

```
/
├── .github/workflows/       # CI/CD (Cloudflare deployment)
├── .windsurf/rules/         # IDE rules (design-system.md)
├── apps/
│   └── frontend/            # Next.js application
├── backend/                 # Python/FastAPI backend
├── mcp/                     # MCP server
├── packages/
│   └── shared/              # @agentpress/shared package
├── .planning/               # GSD planning documents
├── Makefile                 # Build/dev commands
├── AGENTS.md                # Project documentation
├── CONTRIBUTING.md          # Contribution guidelines
├── README.md                # Project overview
├── mcp.json                 # MCP server configuration
├── package.json             # Root monorepo config
├── pnpm-lock.yaml           # Lockfile
└── .npmrc                   # npm config
```

## Backend Structure (`backend/`)

```
backend/
├── api.py                   # FastAPI app entry point, router registration
├── api/v1/
│   └── reports.py           # Reports API
├── agents/                  # Top-level agent modules
│   ├── alternatives_api.py  # Material alternatives REST API
│   ├── alternatives_engine.py
│   ├── scenario_api.py      # Scenario analysis REST API
│   └── scenario_engine.py
├── auth/                    # Auth module
├── boq/                     # Bill of Quantities (mostly empty)
├── config/
│   └── graphdb/             # GraphDB configuration
├── core/                    # Main application logic
│   ├── admin/               # Admin APIs (8 modules)
│   ├── agentpress/          # LLM orchestration framework
│   │   ├── context_manager.py
│   │   ├── error_processor.py
│   │   ├── mcp_registry.py
│   │   ├── native_tool_parser.py
│   │   ├── processor_config.py
│   │   ├── prompt_caching.py
│   │   ├── tool.py
│   │   ├── tool_registry.py
│   │   └── xml_tool_parser.py
│   ├── agents/              # Multi-agent system (20+ files)
│   ├── ai_models/           # LLM model registry
│   ├── analytics/           # Conversation analytics
│   ├── api_models/          # Pydantic API models
│   ├── auth/                # Core auth logic
│   ├── billing/             # Stripe billing
│   ├── cache/               # Runtime caching
│   ├── carbon/              # Carbon calculation API
│   ├── categorization/      # Content categorization
│   ├── chat/                # Chat API
│   ├── composio_integration/ # Composio bridge (8 files)
│   ├── config/              # Configuration (5 modules)
│   ├── credentials/         # API key management
│   ├── endpoints/           # REST endpoints (11 files)
│   ├── files/               # File handling
│   ├── google/              # Google integration
│   ├── jit/                 # JIT execution
│   ├── knowledge_base/      # Document KB
│   ├── knowledge_graph/     # RDF/TGO graph + versioning
│   ├── mcp_module/          # MCP integration
│   ├── memory/              # AI memory (7 files)
│   ├── middleware/           # Rate limiting
│   ├── notifications/       # User notifications
│   ├── prompts/             # Prompt templates
│   ├── referrals/           # Referral system
│   ├── resources/           # Resource types/service
│   ├── sandbox/             # Code execution sandbox
│   ├── services/            # Shared services (Redis, Supabase, etc.)
│   ├── setup/               # Onboarding setup
│   ├── templates/           # Agent templates
│   ├── test_harness/        # Test harness
│   ├── threads/             # Conversation threads
│   ├── tools/               # Agent tools
│   ├── triggers/            # Event triggers
│   ├── utils/               # Utilities
│   └── versioning/          # Data versioning
├── db/models/               # Database models (agent_trace.py)
├── lca/                     # Life Cycle Assessment engine
│   ├── brightway_config.py
│   ├── carbon_calculator.py
│   ├── material_matcher.py
│   ├── unit_converter.py
│   └── tests/               # LCA-specific tests
└── tests/                   # Backend tests
    ├── api/
    ├── boq/
    └── utils/
```

## Frontend Structure (`apps/frontend/`)

```
apps/frontend/
├── prisma/schema.prisma     # Database schema
├── next.config.ts           # Next.js configuration
├── playwright.config.ts     # E2E test configuration
├── postcss.config.mjs       # PostCSS/Tailwind
├── components.json          # shadcn/ui config
├── wrangler.toml            # Cloudflare Workers config
├── vercel.json              # Vercel deployment config
├── Dockerfile*              # 8 Docker variants
├── public/                  # Static assets (SVGs, icons, manifest)
├── scripts/                 # Build scripts
├── translations/            # i18n translations
├── e2e/                     # Playwright E2E tests
│   └── infrastructure/      # Test helpers
├── e2e-report/              # HTML test reports
├── e2e-screenshots/         # Test failure screenshots
└── src/
    ├── app/                 # Next.js App Router
    │   ├── (dashboard)/     # Protected pages
    │   │   ├── admin/
    │   │   ├── agents/
    │   │   ├── credits-explained/
    │   │   ├── dashboard/
    │   │   ├── files/
    │   │   ├── knowledge/
    │   │   ├── onboarding-demo/
    │   │   ├── projects/
    │   │   ├── settings/
    │   │   ├── thread/
    │   │   └── triggers/
    │   ├── (home)/          # Public pages
    │   │   ├── about/ pricing/ careers/ support/ etc.
    │   ├── (public)/        # Brand pages
    │   ├── api/             # Next.js API routes
    │   │   └── health/ integrations/ og/ share-page/ triggers/ v1/
    │   ├── auth/            # Auth flows
    │   └── checkout/ subscription/ etc.
    ├── components/          # UI components
    │   ├── ui/              # 74 shadcn/ui components
    │   ├── thread/          # Chat/thread UI
    │   ├── agents/          # Agent config/management
    │   ├── dashboard/       # Dashboard widgets
    │   └── [20+ domains]    # Organized by feature
    ├── hooks/               # Custom React hooks (127 files)
    │   ├── agents/ auth/ billing/ threads/ etc.
    ├── lib/                 # Utility libraries
    │   ├── analytics/ api/ constants/ icons/ shared/ streaming/ supabase/ utils/
    ├── stores/              # Zustand stores
    ├── styles/              # Global styles
    ├── types/               # TypeScript type definitions
    ├── i18n/                # Internationalization
    ├── assets/              # Animations, images
    └── __tests__/           # Unit tests
```

## Shared Package (`packages/shared/`)

```
packages/shared/
├── src/
│   ├── index.ts             # Main entry
│   ├── types/               # Shared type definitions
│   ├── streaming/           # SSE/streaming utilities
│   ├── tools/               # Tool type definitions
│   ├── utils/               # Shared utilities
│   ├── animations/          # Shared animation components
│   ├── constants/           # Upload limits, etc.
│   └── errors/              # Error types
└── design-system/           # Design system assets
```

## Key File Locations

| Purpose | Path |
|---------|------|
| Backend entry point | `backend/api.py` |
| Frontend entry point | `apps/frontend/src/app/layout.tsx` |
| DB Schema | `apps/frontend/prisma/schema.prisma` |
| Agent definitions | `backend/core/agents/` |
| Carbon calculation | `backend/lca/carbon_calculator.py`, `backend/core/carbon/` |
| Carbon REST API | `backend/core/carbon/api.py` |
| LLM orchestration | `backend/core/agentpress/` |
| Auth config | `backend/core/auth/auth.py` |
| Frontend auth | `apps/frontend/src/app/auth/` |
| Design tokens | `.windsurf/rules/design-system.md` |
| MCP server | `mcp/test_server.py` |
| CI/CD | `.github/workflows/cloudflare.yml` |
