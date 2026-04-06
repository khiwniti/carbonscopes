# Architecture

**Analysis Date:** 2026-04-06

## Pattern Overview

**Overall:** Monorepo with Full-Stack Separation (Next.js Frontend + FastAPI Backend)

**Key Characteristics:**
- Monorepo workspace structure with pnpm for dependency management
- Clear separation between frontend (Next.js 15 App Router) and backend (FastAPI Python)
- Microservices-oriented backend with modular domain boundaries
- Client-server architecture with RESTful API communication
- Real-time capabilities via Supabase subscriptions and SSE streaming
- Multi-platform support (web, desktop, mobile)

## Layers

**Frontend Layer (Next.js 15):**
- Purpose: User interface and client-side state management
- Location: `apps/frontend/`
- Contains: React components, pages, API routes, client state stores
- Depends on: Backend API (`NEXT_PUBLIC_BACKEND_URL`), Supabase client
- Used by: End users via browsers, Desktop app (Electron), Mobile app (React Native)
- Pattern: App Router with route groups, Server/Client Components, RSC

**Backend Layer (FastAPI):**
- Purpose: Business logic, API endpoints, data orchestration
- Location: `backend/`
- Contains: REST endpoints, domain services, database repositories
- Depends on: Supabase (PostgreSQL), Redis, external APIs (LLMs, integrations)
- Used by: Frontend applications, API consumers
- Pattern: Domain-driven modular structure with layered services

**Data Layer:**
- Purpose: Persistent storage and caching
- Technologies: Supabase (PostgreSQL), Redis (caching/rate limiting), Qdrant (vector DB)
- Depends on: Cloud infrastructure (Azure/Supabase cloud)
- Used by: Backend services
- Pattern: Repository pattern with connection pooling

**Agent Execution Layer:**
- Purpose: AI agent orchestration and LLM interactions
- Location: `backend/core/agentpress/`, `backend/core/agents/`
- Contains: Thread management, tool execution, streaming responses
- Depends on: LLM providers (OpenAI, Anthropic), sandboxed execution environments
- Used by: Backend API layer
- Pattern: Event-driven with streaming generators

**Integration Layer:**
- Purpose: External service connections and third-party APIs
- Location: `backend/core/composio_integration/`, `backend/core/services/`
- Contains: API clients, webhooks, authentication handlers
- Depends on: External APIs (Stripe, Langfuse, Google Analytics, etc.)
- Used by: Backend services
- Pattern: Client abstractions with error handling

## Data Flow

**User Request → Response Flow:**

1. User interacts with Next.js frontend (browser/app)
2. Client-side React Query manages API state and caching
3. Request sent to `/api/v1/*` via `api-client.ts` with Supabase JWT auth
4. Next.js rewrites proxy to backend or direct backend call
5. FastAPI backend receives request, validates JWT via Supabase
6. Rate limiting middleware (slowapi) checks request limits
7. Business logic executes in domain-specific service modules
8. Database operations via Supabase async client with connection pooling
9. Response returned (JSON or SSE stream for agent interactions)
10. Frontend updates UI via React Query cache invalidation

**Agent Execution Flow:**

1. User sends message via thread interface
2. Frontend creates message in database, initiates agent run
3. Backend `ThreadManager` fetches conversation history
4. Agent orchestration via `ExecutionOrchestrator` with tool registry
5. LLM generates response with potential tool calls
6. Tools execute (file operations, API calls, code execution)
7. Streaming response chunks sent via SSE to frontend
8. Frontend renders incremental updates in real-time
9. Billing tracked per token usage, checkpoints saved
10. Thread state persisted with vector embeddings for context

**State Management:**
- Client: Zustand stores for UI state, React Query for server state
- Server: PostgreSQL for persistence, Redis for ephemeral state/caching
- Real-time: Supabase subscriptions for live updates across clients

## Key Abstractions

**ThreadManager:**
- Purpose: Core orchestration for AI agent conversations
- Examples: `backend/core/agentpress/thread_manager/manager.py`
- Pattern: Async manager with service composition (MessageFetcher, ExecutionOrchestrator, BillingHandler)
- Responsibilities: Thread lifecycle, message persistence, streaming execution, auto-continuation

**ApiClient:**
- Purpose: Type-safe HTTP client with authentication and error handling
- Examples: `apps/frontend/src/lib/api-client.ts`
- Pattern: Wrapper around fetch with interceptors for auth headers, timeout management
- Features: Automatic JWT injection, error parsing, timeout control, FormData support

**ToolRegistry:**
- Purpose: Dynamic tool registration and execution for agents
- Examples: `backend/core/agentpress/tool_registry.py`, `backend/core/agentpress/tool.py`
- Pattern: Registry pattern with reflection-based function discovery
- Capabilities: Native Python tools, MCP server tools, XML/JSON schema generation

**DBConnection (Singleton):**
- Purpose: Per-worker database connection with HTTP/2 multiplexing
- Examples: `backend/core/services/supabase.py`
- Pattern: Thread-safe singleton with connection pooling stats
- Architecture: 8-16 Gunicorn workers × 100 HTTP/2 streams = 800 concurrent requests per container

**ComponentStore (Zustand):**
- Purpose: Client-side reactive state management
- Examples: `apps/frontend/src/stores/thread-navigation-store.ts`
- Pattern: Zustand with selector-based subscriptions for performance
- Features: Persistent state (localStorage), optimistic updates, devtools integration

## Entry Points

**Frontend Entry:**
- Location: `apps/frontend/src/app/layout.tsx`
- Triggers: Browser navigation, initial page load
- Responsibilities: Root layout, provider tree setup, analytics initialization, SEO metadata

**Backend Entry:**
- Location: `backend/api.py`
- Triggers: HTTP requests via Gunicorn/Uvicorn
- Responsibilities: FastAPI app initialization, middleware setup, router registration, lifespan management

**Agent Execution Entry:**
- Location: `backend/core/agentpress/thread_manager/manager.py:run_thread()`
- Triggers: User message submission, agent invocation
- Responsibilities: Message history retrieval, LLM streaming, tool execution, billing tracking

**Desktop App Entry:**
- Location: `apps/desktop/` (Electron)
- Triggers: Native app launch
- Responsibilities: Window management, system integration, embedded frontend webview

**Mobile App Entry:**
- Location: `apps/mobile/` (React Native)
- Triggers: Mobile app launch
- Responsibilities: Native navigation, platform-specific UI, shared business logic

## Error Handling

**Strategy:** Multi-layered error handling with user-friendly messages

**Patterns:**
- Frontend: `error-handler.ts` with toast notifications and error boundaries
- Backend: FastAPI exception handlers with structured error responses
- Agent Layer: `ErrorProcessor` for tool execution failures with retry logic
- Network: Timeout handling with AbortController, exponential backoff for retries

**Error Flow:**
1. Exception occurs in backend service
2. FastAPI middleware catches and formats as JSON error response
3. Frontend `api-client.ts` intercepts HTTP error
4. `handleApiError()` parses error details and shows toast notification
5. React Error Boundaries catch rendering errors and show fallback UI
6. Sentry/monitoring captures errors for analysis (optional)

**Special Cases:**
- 402 Payment Required → Parsed as `TierRestrictionError` with upgrade prompts
- 431 Headers Too Large → `RequestTooLargeError` with file upload guidance
- Rate limit (429) → Custom rate limit handler with retry-after headers
- JWT expiration → Automatic token refresh via Supabase client

## Cross-Cutting Concerns

**Logging:**
- Frontend: `logger.ts` with PostHog integration for user events
- Backend: `structlog` with structured JSON logging, CloudWatch integration
- Agents: Per-agent logging with Langfuse tracing for LLM observability

**Validation:**
- Frontend: Zod schemas with `react-hook-form` integration
- Backend: Pydantic models for request/response validation
- Database: PostgreSQL constraints and Supabase RLS policies

**Authentication:**
- Strategy: Supabase Auth with JWT tokens
- Frontend: `AuthProvider` context with automatic token refresh
- Backend: `verify_and_get_user_id_from_jwt()` middleware
- Flow: OAuth (Google/GitHub) or magic link → JWT issued → validated on each API request

**Caching:**
- Client: React Query with stale-while-revalidate strategy
- Server: Redis for rate limiting, session data, temporary computation results
- Database: Supabase connection pooling with HTTP/2 multiplexing
- CDN: Static assets cached via Vercel/Azure CDN

**Rate Limiting:**
- Implementation: `slowapi` middleware with Redis backend
- Limits: Per-IP and per-user tiers (free, pro, enterprise)
- Response: 429 status with `Retry-After` header
- Bypass: Development mode bypasses for local testing

**Internationalization:**
- Library: `next-intl` for translations
- Storage: Translation files in `apps/frontend/translations/`
- Detection: Browser locale → localStorage → cookie → default 'en'
- Provider: `I18nProvider` wraps app with locale context

**Analytics:**
- PostHog: User behavior tracking, feature flags, A/B testing
- Google Analytics 4: Via GTM for marketing attribution
- Langfuse: LLM-specific observability (latency, tokens, costs)
- Prometheus: Backend metrics (requests/sec, latency, errors)

**Feature Flags:**
- System: `feature-flags.ts` for client-side feature toggles
- Edge Flags: Vercel Edge Config for dynamic server-side flags
- Agent Config: Per-agent configuration for model selection, tool availability

---

*Architecture analysis: 2026-04-06*
