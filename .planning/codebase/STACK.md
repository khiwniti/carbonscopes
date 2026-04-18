# CarbonScopes Technology Stack

> Mapped: 2026-04-18

## Languages

| Language | Runtime/Version | Primary Use |
|----------|----------------|-------------|
| Python | 3.11+ | Backend API, agents, LCA calculations |
| TypeScript | 5.x | Frontend (Next.js), shared package |
| SQL | PostgreSQL | Database (via Prisma ORM + Supabase) |
| SPARQL | — | Knowledge graph queries (TGO/RDF) |

## Backend Stack

### Framework & Server
- **FastAPI** 0.115.12 — REST API framework
- **Uvicorn** 0.27.1 — ASGI server
- **Gunicorn** >=23.0.0 — Production WSGI server

### AI / LLM
- **LiteLLM** >=1.80.11 — Multi-model LLM gateway
- **OpenAI** >=1.99.5 — OpenAI API client
- **LangFuse** 2.60.5 — LLM observability/tracing
- **MCP** 1.9.4 — Model Context Protocol server

### Carbon / LCA Domain
- **Brightway2** (via `backend/lca/`) — Life cycle assessment calculations
- Custom deterministic carbon calculator: `backend/core/carbon/brightway/calculator.py`
- RDF/SPARQL knowledge graph for TGO material data

### Data & Storage
- **Supabase** 2.17.0 — PostgreSQL database (hosted)
- **Prisma** 0.15.0 — ORM (Python client, schema at `apps/frontend/prisma/schema.prisma`)
- **Redis** 5.2.1 / **Upstash Redis** 1.3.0 — Caching, rate limiting
- **RDFLib** — In-memory graph DB with optional GraphDB integration

### Auth & Security
- **PyJWT** 2.10.1 — JWT token handling
- **Cryptography** >=41.0.0 — Encryption utilities
- **Email Validator** 2.0.0

### Integrations
- **Composio** >=0.8.0 — Third-party tool/action integration platform
- **E2B Code Interpreter** 1.2.0 — Sandboxed code execution
- **Daytona SDK** >=0.115.0 — Development environment management
- **Stripe** 11.6.0 — Payment processing
- **Tavily** 0.5.4 — Web search
- **Exa** >=1.14.0 — Search API
- **Replicate** >=0.25.0 — AI model inference
- **VNCDoTool** 1.2.0 — Remote desktop automation
- **Apify** — Web scraping (frontend hooks)
- **Mailtrap** 2.0.0 — Email delivery
- **Novu** ^3.11.0 — Notification center (frontend)
- **Cal.com Embed** ^1.5.2 — Scheduling (frontend)

### Utilities
- **structlog** 25.4.0 — Structured logging
- **APScheduler** >=3.10.0 — Background job scheduling
- **Prometheus Client** 0.21.1 — Metrics
- **PyPDF2**, **python-docx**, **openpyxl**, **python-pptx** — Document processing
- **BeautifulSoup4** >=4.12.0 — HTML parsing
- **WeasyPrint** >=63.0 — PDF generation
- **Pillow** >=10.4.0 — Image processing
- **pytesseract** 0.3.13 — OCR

### Testing (Backend)
- **pytest** 8.3.4 + asyncio, cov, mock, xdist, timeout, randomly, rerunfailures

## Frontend Stack

### Framework
- **Next.js** 15.x — React framework (App Router)
- **React** ^19.1.0 — UI library
- **TypeScript** 5.x

### State & Data
- **Zustand** ^5.0.9 — Client state management
- **TanStack React Query** ^5.97.0 — Server state / data fetching
- **TanStack React Table** 8.21.3 — Table component

### UI Components
- **Radix UI** — 20+ primitives (accordion, alert-dialog, avatar, checkbox, collapsible, context-menu, etc.)
- **shadcn/ui** — Component library (`apps/frontend/components.json`)
- **Tailwind CSS** — Styling (via PostCSS)
- **CodeMirror** 6 — Code editor
- **dnd-kit** — Drag and drop
- **Floating UI** — Positioning/tooltip
- **Emoji Mart** — Emoji picker
- **Number Flow** — Animated numbers
- **HugeIcons React** — Icon library
- **Icons Pack React Simple Icons** — Brand icons

### Auth & Supabase (Frontend)
- **NextAuth.js** — Authentication (Google, GitHub OAuth)
- **Supabase JS Client** — Direct DB access from frontend

### E2E Testing
- **Playwright** — Browser automation testing

## Shared Package
- **@agentpress/shared** v1.0.0 — Shared types, streaming, tools, utils, animations, constants, errors
- Exports: types, streaming, tools, utils, animations, constants, errors

## Build & Deployment
- **pnpm** 9.x — Package manager (monorepo)
- **Docker** — Multiple Dockerfiles (build, runtime, production, minimal, standalone, prebuilt, simple)
- **Cloudflare Workers/Pages** — Deployment target
- **Vercel** — Alternative deployment (`vercel.json` present)
- **GitHub Actions** — CI/CD (`.github/workflows/cloudflare.yml`)

## Configuration
- `.env.local.template` — Frontend env template (DATABASE_URL, NEXTAUTH, OAuth, API_URL)
- `backend/core/config/` — Backend config modules:
  - `carbonscope_config.py` — App-specific config
  - `suna_config.py` — General platform config
  - `timeouts.py` — Timeout settings
  - `vapi_config.py` — Voice API config
  - `config_helper.py` — Config utilities
