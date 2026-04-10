# External Integrations

**Analysis Date:** 2026-04-09

## APIs & External Services

**AI/LLM Providers:**
- OpenAI - GPT models via LiteLLM wrapper
  - SDK/Client: litellm package
  - Auth: OPENAI_API_KEY environment variable
- Anthropic - Claude models via LiteLLM wrapper
  - SDK/Client: litellm package
  - Auth: ANTHROPIC_API_KEY environment variable
- Azure OpenAI - Azure-hosted OpenAI models via LiteLLM
  - SDK/Client: litellm package
  - Auth: AZURE_API_KEY, AZURE_API_BASE, AZURE_API_VERSION
- AWS Bedrock - Anthropic Claude via Bedrock
  - SDK/Client: litellm package with bedrock/* model prefixes
  - Auth: AWS_BEARER_TOKEN_BEDROCK environment variable
- OpenRouter - Aggregated LLM access via LiteLLM
  - SDK/Client: litellm package
  - Auth: OPENROUTER_API_KEY environment variable
- Gemini - Google models via LiteLLM (configured but less prominent)
  - SDK/Client: litellm package
  - Auth: GOOGLE_API_KEY environment variable

**Data Storage & Databases:**
- Supabase - Primary PostgreSQL database, authentication, and storage
  - SDK/Client: supabase-py (version 2.17.0)
  - Auth: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_ANON_KEY)
  - Used for: User data, agent states, threads, billing, configurations
- Upstash Redis - Redis compatibility layer (used alongside direct Redis)
  - SDK/Client: upstash-redis package
  - Auth: UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN
  - Used for: Fallback/caching layer
- Qdrant - Vector database for embeddings and similarity search
  - SDK/Client: qdrant-client package (version >=1.11.0)
  - Auth: QDRANT_URL and QDRANT_API_KEY environment variables
  - Used for: Knowledge graph embeddings, semantic search

**File Storage:**
- Supabase Storage - Object storage for files, documents, exports
  - Integrated via Supabase client
  - Used for: Agent outputs, reports, uploads
- AWS S3 - Binary Large Object storage (via boto3)
  - SDK/Client: boto3 package (version >=1.40.74)
  - Auth: AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION
  - Used for: Large file storage, backups, media assets

**Caching:**
- Redis (Upstash/self-hosted) - Primary caching layer
  - SDK/Client: redis package (version 5.2.1) with custom StreamHub implementation
  - Auth: REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_USERNAME, REDIS_SSL
  - Used for: Session caching, rate limiting, SSE fan-out, temporary agent state

## Authentication & Identity

**Auth Provider:**
- Supabase Auth - Built-in authentication service
  - Implementation: JWT-based via Supabase GoTrue
  - Integration: @supabase/supabase-js (frontend), supabase-py (backend)
  - Features: Email/password, magic links, OAuth providers (Google, GitHub, etc.)
  - Environment: SUPABASE_URL, SUPABASE_ANON_KEY (client-side), SUPABASE_SERVICE_ROLE_KEY (admin)

**Additional Auth:**
- FastAPI Users/OAuth2 - Supplemental auth patterns in custom endpoints
- Apple Authentication - Expo Apple Authentication module (mobile)
  - SDK: expo-apple-authentication
  - Used for: iOS/macOS authentication via Apple ID

## Monitoring & Observability

**Error Tracking:**
- Braintrust - LLM experimentation and evaluation tracking
  - Integration: Automatic via litellm when BRAINTRUST_API_KEY is set
  - Used for: LLM prompt/response logging, evaluation datasets
- Sentry - Error tracking (configured but not heavily used in current codebase)
  - Implied via sentry-sdk references in some tool backups

**Logging:**
- Structlog - Structured logging for backend
  - Configuration: JSON output to stdout/stderr
  - Shipping: Configured to send to CloudWatch Logs in production via watchtower
- CloudWatch Logs - AWS logging service
  - Integration: watchtower >=3.0.0 package
  - Used for: Production log aggregation and monitoring

**Metrics & Tracing:**
- Prometheus Client - Metrics exposition
  - SDK: prometheus-client package (version 0.21.1)
  - Endpoint: /metrics (exposes agent runs, Redis stats, system metrics)
- Custom Metrics - Internal metrics collection
  - Implementation: Worker metrics service tracking agent runs, Redis streams, memory usage

## CI/CD & Deployment

**Hosting:**
- Linux Containers - Docker-based deployment
  - Configuration: Dockerfiles in backend/, apps/frontend/, etc.
  - Orchestration: Kubernetes or similar (implied by health checks and replica concepts)
- Vercel - Frontend hosting (for Next.js applications)
  - Configuration: next.config.ts, vercel.json or similar
  - Environment variables injected via Vercel dashboard
- Electron Builder - Desktop application packaging
  - Configuration: apps/desktop/package.json build section
  - Targets: macOS (dmg), Windows (nsis), Linux (AppImage)
- EAS (Expo Application Services) - Mobile app builds
  - Configuration: app.json, eas.json
  - Used for: Android/iOS store builds

**CI Pipeline:**
- GitHub Actions - Implied CI/CD (workflows not visible in current repo snapshot)
- Local Scripts - Package.json scripts for development:
  - dev:frontend, dev:mobile, dev:backend
  - build:frontend, build:mobile
  - docker compose up -d (for full stack)
- Makefile - Monorepo-level commands:
  - make install, make dev-backend, make dev-frontend

## Environment Configuration

**Required env vars:**
- SUPABASE_URL - Supabase project URL
- SUPABASE_SERVICE_ROLE_KEY - Supabase service role key (backend)
- SUPABASE_ANON_KEY - Supabase anon key (frontend)
- DATABASE_URL - Direct PostgreSQL connection string (alternative to Supabase)
- REDIS_HOST - Redis hostname
- REDIS_PORT - Redis port (default 6379)
- REDIS_PASSWORD - Redis password (if set)
- ANTHROPIC_API_KEY - Anthropic API key (for Claude models)
- OPENAI_API_KEY - OpenAI API key (for GPT models)
- OPENROUTER_API_KEY - OpenRouter API key (optional alternative)
- AWS_BEARER_TOKEN_BEDROCK - AWS Bedrock token (for Claude via Bedrock)
- QDRANT_URL - Qdrant vector database URL
- QDRANT_API_KEY - Qdrant API key

**Secrets location:**
- .env files - Local development (backend/.env, apps/frontend/.env.local)
- Platform secret managers - Production (Vercel Env, Docker secrets, K8s secrets)
- Doppler/AWS Secrets Manager - Referenced in documentation but not visible in code

## Webhooks & Callbacks

**Incoming:**
- Supabase Webhooks - Database change triggers
  - Endpoint: /api/webhooks/* (handled by webhook_router)
  - Used for: Real-time updates to frontend via Redis streams
- Stripe Webhooks - Payment processing
  - Endpoint: /api/webhooks/* (specific handlers in setup/webhook_router)
  - Used for: Subscription events, payment confirmations
- GitHub Webhooks - Repository events (for integrations)
  - Endpoint: /api/webhooks/* (generic handling)
- Calendar/Webhook Integrations - External service callbacks
  - Endpoint: /api/webhooks/* (configurable per integration)

**Outgoing:**
- Novu - Notification delivery service
  - Endpoints: Novu API (hosted)
  - Used for: Email, SMS, push notifications via novu-py SDK
- Email Services - SMTP/SendGrid/etc. (via mailtrap in dev)
  - SDK: mailtrap package
  - Used for: Transactional emails, alerts
- Calendar APIs - Google Calendar, Outlook (via composio or direct)
  - Used for: Scheduling, meeting creation
- Slack/Teams - Team notifications (via composio integrations)
  - SDK: composio package
  - Used for: Alert distribution, team collaboration

---

*Integration audit: 2026-04-09*