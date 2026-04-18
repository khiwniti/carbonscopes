# CarbonScopes Integrations

> Mapped: 2026-04-18

## External APIs

### AI / LLM Services
| Service | Library | Purpose | Backend Location |
|---------|---------|---------|------------------|
| OpenAI | `openai` >=1.99.5 | LLM inference, embeddings | `backend/core/ai_models/` |
| LiteLLM | `litellm` >=1.80.11 | Multi-provider LLM gateway | `backend/core/agentpress/` |
| Replicate | `replicate` >=0.25.0 | AI model inference | `backend/core/agents/` |
| Tavily | `tavily-python` 0.5.4 | Web search for agents | `backend/core/agents/` |
| Exa | `exa-py` >=1.14.0 | Search API | — |

### Authentication & Identity
| Service | Protocol | Purpose | Location |
|---------|----------|---------|----------|
| Google OAuth | OAuth2 | User authentication | Frontend NextAuth (`apps/frontend/src/app/auth/`) |
| GitHub OAuth | OAuth2 | User authentication | Frontend NextAuth (`apps/frontend/src/app/auth/callback/`) |
| Supabase Auth | JWT | Session management, DB auth | `backend/core/auth/auth.py`, `backend/core/services/supabase.py` |
| PyJWT | JWT | Token signing/verification | `backend/core/auth/` |

### Payment & Billing
| Service | Library | Purpose | Location |
|---------|---------|---------|----------|
| Stripe | `stripe` 11.6.0 | Payment processing, subscriptions | `backend/core/billing/api.py` |

### Communication
| Service | Library | Purpose | Location |
|---------|---------|---------|----------|
| Mailtrap | `mailtrap` 2.0.0 | Transactional email | `backend/core/notifications/` |
| Novu | `@novu/nextjs` ^3.11.0 | In-app notification center | `apps/frontend/src/components/notifications/` |
| Cal.com | `@calcom/embed-react` | Scheduling embed | Frontend |

### Database & Storage
| Service | Library | Purpose | Location |
|---------|---------|---------|----------|
| Supabase | `supabase` 2.17.0 | PostgreSQL database hosting | `backend/core/services/supabase.py` |
| Redis / Upstash | `redis` 5.2.1 / `upstash-redis` 1.3.0 | Caching, rate limiting, sessions | `backend/core/services/redis.py`, `backend/core/middleware/rate_limit.py` |
| GraphDB / RDFLib | RDFLib | Knowledge graph for TGO materials | `backend/core/knowledge_graph/`, `backend/core/services/graphdb.py` |

### Sandbox & Execution
| Service | Library | Purpose | Location |
|---------|---------|---------|----------|
| E2B | `e2b-code-interpreter` 1.2.0 | Sandboxed code execution | `backend/core/sandbox/` |
| Daytona | `daytona-sdk` >=0.115.0 | Dev environment management | `backend/core/sandbox/` |

### Integration Platform
| Service | Library | Purpose | Location |
|---------|---------|---------|----------|
| Composio | `composio` >=0.8.0 | Third-party tool integrations, triggers | `backend/core/composio_integration/` (8 modules) |

### Monitoring & Observability
| Service | Library | Purpose | Location |
|---------|---------|---------|----------|
| LangFuse | `langfuse` 2.60.5 | LLM trace/logging | `backend/core/agentpress/` |
| Prometheus | `prometheus-client` 0.21.1 | Application metrics | `backend/core/utils/` |
| PostHog | `posthog-js` | Product analytics | Frontend (CSP config) |

## Webhooks
| Source | Endpoint | Purpose |
|--------|----------|---------|
| Stripe | `/webhooks/stripe` | Payment events |
| VAPI | `/v1/vapi/webhooks` | Voice AI events (`backend/core/endpoints/vapi_webhooks.py`) |
| Composio | Triggers system | Third-party event triggers (`backend/core/triggers/`) |
| GitHub Actions | CI/CD webhook | Deployment triggers |

## MCP (Model Context Protocol)
- **MCP Server**: Python-based at `mcp/test_server.py`
- **Config**: `mcp.json` defines server connection
- **Client SDK**: `mcp` 1.9.4 in backend
- **Registry**: `backend/core/agentpress/mcp_registry.py`

## Internal API Endpoints
- **Backend API**: FastAPI on port 8000 (`NEXT_PUBLIC_API_URL`)
- **Frontend API Routes**: Next.js API routes at `apps/frontend/src/app/api/`
  - `/api/health`, `/api/integrations`, `/api/og`, `/api/share-page`, `/api/triggers`, `/api/v1`
- **Carbon API**: `/v1/tgo/load`, `/v1/carbon/calculate`, `/v1/certify/edge`, `/v1/certify/trees`
