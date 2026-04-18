# CarbonScopes Architecture

> Mapped: 2026-04-18

## High-Level Pattern

**Monorepo with separated backend/frontend + shared package**

```
┌─────────────────────────────────────────────────────┐
│                   Client Browser                      │
│              Next.js App Router (React 19)            │
├─────────────────────────────────────────────────────┤
│  Pages/ Routes    │  Components   │  Hooks  │ Stores │
│  (App Router)     │  (shadcn/ui)  │ (SWR)   │(Zustand)│
├─────────────────────────────────────────────────────┤
│           @agentpress/shared (types, utils)           │
├─────────────────────────────────────────────────────┤
│              Next.js API Routes (/api/*)              │
│           + Supabase Client Direct Access             │
└────────────────────┬────────────────────────────────┘
                     │ HTTP / SSE
┌────────────────────▼────────────────────────────────┐
│              FastAPI Backend (Port 8000)               │
├──────────┬──────────┬───────────┬───────────────────┤
│  Auth    │  Agents  │  Carbon   │  Admin / Billing  │
│  Layer   │  System  │  Engine   │  / Monitoring     │
├──────────┴──────────┴───────────┴───────────────────┤
│             AgentPress (LLM Orchestration)            │
│  ┌─────────┐ ┌──────────┐ ┌───────────────────┐     │
│  │Thread   │ │Tool      │ │Prompt Caching     │     │
│  │Manager  │ │Registry  │ │Context Manager    │     │
│  └─────────┘ └──────────┘ └───────────────────┘     │
├─────────────────────────────────────────────────────┤
│  Supabase (PostgreSQL)  │  Redis/Upstash  │ GraphDB │
└─────────────────────────────────────────────────────┘
```

## Backend Architecture

### Entry Point
- `backend/api.py` — FastAPI application setup, CORS, router registration, lifespan management

### Core Layer (`backend/core/`)
Domain-organized modules following a service/API/repository pattern:

| Module | Purpose | Key Files |
|--------|---------|-----------|
| `agents/` | Multi-agent AI system | `agent_service.py`, `supervisor.py`, `router.py`, `base.py` |
| `agentpress/` | LLM orchestration framework | `thread_manager.py`, `tool_registry.py`, `context_manager.py` |
| `carbon/` | Carbon calculation endpoints | `api.py`, `audit.py` |
| `auth/` | Authentication logic | `auth.py` |
| `billing/` | Stripe payment integration | `api.py` |
| `chat/` | Chat/messaging endpoints | `api.py` |
| `threads/` | Conversation thread management | `api.py` |
| `sandbox/` | Code execution environments | `api.py` |
| `knowledge_base/` | Document ingestion | `api.py`, `file_processor.py` |
| `knowledge_graph/` | RDF/TGO material graph | `tgo_loader.py`, versioning |
| `memory/` | AI memory/extraction | `extraction_service.py`, `retrieval_service.py` |
| `composio_integration/` | Third-party tool bridge | 8 service modules |
| `credentials/` | API key management | `credential_service.py`, `profile_service.py` |
| `notifications/` | User notifications | `api.py` |
| `triggers/` | Event trigger system | `api.py` |
| `files/` | File upload/management | — |
| `templates/` | Agent templates | `api.py`, `template_service.py` |
| `analytics/` | Conversation analytics | Workers, clustering |
| `categorization/` | Content categorization | `service.py`, background jobs |
| `admin/` | Admin panel APIs | 8 admin API modules |
| `endpoints/` | Miscellaneous REST endpoints | `carbon_api.py`, `boq_api.py`, `export_api.py` |

### Agent System (`backend/core/agents/`)
LangGraph-style multi-agent architecture with specialized agents:

| Agent | Purpose |
|-------|---------|
| `supervisor.py` | Orchestrates agent routing |
| `carbon_calculator.py` | Calculates embodied carbon from BOQ |
| `material_analyst.py` | Analyzes construction materials |
| `compliance_agent.py` | EDGE/TREES certification checks |
| `sustainability_agent.py` | Sustainability recommendations |
| `boq_parser_agent.py` | Parses Bill of Quantities documents |
| `cost_analyst_agent.py` | Cost analysis |
| `data_validator_agent.py` | Data validation |
| `report_generator_agent.py` | Report generation |
| `knowledge_graph.py` | Knowledge graph queries |
| `alternatives_engine.py` | Material alternatives |

### LCA Engine (`backend/lca/`)
Brightway2-based life cycle assessment:
- `carbon_calculator.py` — Deterministic carbon calculation pipeline
- `brightway_config.py` — Brightway2 configuration
- `material_matcher.py` — Material name matching to LCA databases
- `unit_converter.py` — Unit conversion utilities

### Data Flow
1. User uploads BOQ (Bill of Quantities) via frontend
2. Backend receives file, `boq_parser_agent` extracts materials
3. `material_analyst` categorizes and matches materials
4. `carbon_calculator` computes embodied carbon using Brightway2
5. `compliance_agent` checks EDGE V3 / TREES MR1 certification
6. Results returned via REST API, displayed in dashboard

## Frontend Architecture

### Next.js App Router Structure
Route groups organize pages by access level:
- `(home)/` — Public landing pages (about, pricing, careers, etc.)
- `(public)/` — Brand pages
- `(dashboard)/` — Authenticated user pages (agents, projects, dashboard, settings, thread)
- `auth/` — Authentication flows (callback, password reset, phone verification)
- `api/` — Next.js API routes

### Component Organization
- `src/components/ui/` — 74 shadcn/ui + Radix primitive components
- `src/components/thread/` — Chat/thread UI (carbonscope-computer, chat-input, content, tool-views)
- `src/components/agents/` — Agent configuration, MCP, tools, knowledge base
- `src/components/dashboard/` — Dashboard widgets
- `src/components/auth/` — Auth forms
- `src/components/billing/` — Pricing/payment UI

### State Management
- **Zustand** — Client-side global state
- **TanStack React Query** — Server state, caching, mutations
- Custom hooks in `src/hooks/` (127 hook files organized by domain)

### Data Layer
- **Supabase JS Client** — Direct DB access for some operations
- **Backend API** — `/v1/*` endpoints via `NEXT_PUBLIC_API_URL`
- **Next.js API Routes** — Thin proxies and utility endpoints
