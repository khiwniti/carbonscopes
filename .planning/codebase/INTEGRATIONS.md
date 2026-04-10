# External Integrations

**Analysis Date:** 2026-04-10

## APIs & External Services

**AI/LLM Services:**
- OpenAI - GPT models for AI agents
  - SDK/Client: openai package
  - Auth: OPENAI_API_KEY environment variable
- Anthropic - Claude models for AI agents
  - SDK/Client: anthropic package
  - Auth: ANTHROPIC_API_KEY environment variable
- Langfuse - LLM observability and tracing
  - SDK/Client: langfuse package
  - Auth: LANGFUSE_SECRET_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_HOST
- LiteLLM - Unified LLM API interface
  - SDK/Client: litellm package
  - Auth: Uses provider-specific keys

**Database & Storage:**
- Supabase - PostgreSQL database, authentication, and storage
  - SDK/Client: @supabase/supabase-js (frontend), supabase package (backend)
  - Auth: SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, SUPABASE_JWT_SECRET
- Upstash Redis - Redis caching and session storage
  - SDK/Client: upstash-redis package
  - Auth: UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN
- Qdrant - Vector database for embeddings and similarity search
  - SDK/Client: qdrant-client package
  - Auth: QDRANT_HOST, QDRANT_API_KEY (inferred)

**Payments & Billing:**
- Stripe - Payment processing and subscription management
  - SDK/Client: stripe package (backend), @stripe/stripe-js and @stripe/react-stripe-js (frontend)
  - Auth: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET
- Novu - Notification infrastructure (email, SMS, push, in-app)
  - SDK/Client: novu package (backend), @novu/nextjs and @novu/notification-center (frontend)
  - Auth: NOVU_API_KEY

**Communication & Collaboration:**
- Daytona - Development environment and sandbox management
  - SDK/Client: daytona-sdk, daytona-api-client packages
  - Auth: DAYTONA_API_KEY, DAYTONA_API_URL (inferred)
- Composio - Agent tooling and integration framework
  - SDK/Client: composio package
  - Auth: COMPOSIO_API_KEY (inferred)
- Model Context Protocol (MCP) - Standard for agent-tool interactions
  - SDK/Client: mcp package
  - Auth: No direct auth (protocol level)

**Analytics & Monitoring:**
- PostHog - Product analytics and feature flags
  - SDK/Client: posthog-js (frontend), posthog-node (backend)
  - Auth: POSTHOG_KEY, POSTHOG_HOST
- Vercel Analytics - Web analytics for frontend
  - SDK/Client: @vercel/analytics
  - Auth: Automatically enabled in Vercel deployment
- Vercel Speed Insights - Performance monitoring
  - SDK/Client: @vercel/speed-insights

**Utilities:**
- Exa - Web search API for agents
  - SDK/Client: exa-py package
  - Auth: EXA_API_KEY
- Tavily - Search API for agents
  - SDK/Client: tavily-python package
  - Auth: TAVILY_API_KEY
- Apify - Web scraping and automation platform
  - SDK/Client: apify-client package
  - Auth: APIFY_API_TOKEN
- Reality Defender - Deepfake detection
  - SDK/Client: realitydefender package
  - Auth: REALITY_DEFENDER_API_KEY (inferred)
- Braintrust - LLM evaluation and experimentation
  - SDK/Client: braintrust package
  - Auth: BRAINTRUST_API_KEY (inferred)
- Autoevals - Automatic LLM evaluation
  - SDK/Client: autoevals package
  - Auth: No direct auth required

## Data Storage

**Databases:**
- PostgreSQL (via Supabase)
  - Connection: SUPABASE_URL with postgres credentials
  - Client: Supabase client (JS/TS), SQLAlchemy/Prisma (Python)
- Redis (via Upstash)
  - Connection: UPSTASH_REDIS_REST_URL
  - Client: upstash-redis package

**File Storage:**
- Supabase Storage - File uploads and document storage
- Local filesystem - Used in development and sandbox environments

**Caching:**
- Upstash Redis - Primary caching layer
- In-memory caching - Used for temporary data (inferred from code patterns)

## Authentication & Identity

**Auth Provider:**
- Supabase Auth - Authentication service
  - Implementation: Email/password, OAuth providers (Google, GitHub, etc.), magic links
  - Frontend: @supabase/ssr package for server-side auth
  - Backend: JWT validation using SUPABASE_JWT_SECRET

## Monitoring & Observability

**Error Tracking:**
- Not explicitly detected - May rely on logging and monitoring services

**Logs:**
- Structured logging using structlog package
- CloudWatch integration via watchtower package (for AWS deployments)
- Console logging in development

## CI/CD & Deployment

**Hosting:**
- Multi-target: AWS (ECS/EKS), Azure, Vercel (frontend)
- Docker containers for backend services

**CI Pipeline:**
- GitHub Actions (inferred from .github directory)
- Custom deployment scripts: deploy-azure.sh, deploy-frontend.sh, etc.
- Pulumi for infrastructure provisioning

## Environment Configuration

**Required env vars:**
- SUPABASE_URL - Supabase project URL
- SUPABASE_ANON_KEY - Supabase anonymous key
- SUPABASE_SERVICE_ROLE_KEY - Supabase service role key
- SUPABASE_JWT_SECRET - Supabase JWT secret
- OPENAI_API_KEY - OpenAI API key
- ANTHROPIC_API_KEY - Anthropic API key
- STRIPE_SECRET_KEY - Stripe secret key
- STRIPE_WEBHOOK_SECRET - Stripe webhook secret
- NOVU_API_KEY - Novu API key
- POSTHOG_KEY - PostHog API key
- POSTHOG_HOST - PostHog host
- UPSTASH_REDIS_REST_URL - Upstash Redis REST URL
- UPSTASH_REDIS_REST_TOKEN - Upstash Redis REST token
- QDRANT_HOST - Qdrant host
- QDRANT_API_KEY - Qdrant API key
- EXA_API_KEY - Exa API key
- TAVILY_API_KEY - Tavily API key
- APIFY_API_TOKEN - Apify API token
- DAYTONA_API_KEY - Daytona API key
- BRAINTRUST_API_KEY - Braintrust API key
- COMPOSIO_API_KEY - Composio API key
- REALITY_DEFENDER_API_KEY - Reality Defender API key

**Secrets location:**
- .env files (gitignored)
- External secret managers (AWS Secrets Manager, Azure Key Vault - inferred from deployment scripts)
- Doppler (mentioned in deployment scripts)

## Webhooks & Callbacks

**Incoming:**
- Stripe webhooks - Payment events, subscription changes
- Supabase webhooks - Database changes (via triggers)
- Novu webhooks - Notification delivery status

**Outgoing:**
- Supabase Realtime - Database change subscriptions
- Various API calls to external services (OpenAI, Anthropic, etc.) initiated by application

---

*Integration audit: 2026-04-10*