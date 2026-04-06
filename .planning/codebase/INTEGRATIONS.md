# External Integrations

**Analysis Date:** 2026-04-06

## APIs & External Services

**AI/LLM Providers:**
- Anthropic - Claude API integration via `anthropic` 0.69.0+
  - SDK/Client: `anthropic` Python package
  - Usage: AI agent execution, chat completions
- OpenAI - GPT models via `openai` 1.99.5+
  - SDK/Client: `openai` Python package
  - Usage: Alternative LLM provider
- LiteLLM 1.80.11+ - Multi-provider LLM gateway
  - Purpose: Unified interface across AI providers
  - Abstraction layer for model switching

**Web Search:**
- Tavily - AI-optimized search API
  - SDK/Client: `tavily-python` 0.5.4
  - Usage: Web search tool for agents

**Integration Platforms:**
- Composio 0.8.0+ - Third-party integration platform
  - SDK/Client: `composio` Python package
  - Purpose: Connect to external tools and services
- Apify 2.3.0 - Web scraping and automation
  - SDK/Client: `apify-client`
  - Purpose: Data extraction workflows

**Developer Tools:**
- E2B Code Interpreter 1.2.0 - Sandboxed code execution
  - SDK/Client: `e2b-code-interpreter`
  - Purpose: Safe code execution environment
- Daytona SDK 0.115.0+ - Development environment management
  - Multiple clients: `daytona-sdk`, `daytona-api-client`, `daytona-api-client-async`
  - Purpose: Cloud development environments
- Replicate 0.25.0+ - ML model hosting
  - SDK/Client: `replicate`
  - Purpose: Run AI models via API

## Data Storage

**Databases:**
- Supabase PostgreSQL
  - Connection: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
  - Client: `@supabase/supabase-js` (frontend), `supabase` 2.17.0 (backend)
  - ORM: Prisma 0.15.0 with custom schema
  - Features: PostgreSQL, authentication, real-time subscriptions, storage

**Caching:**
- Redis 5.2.1 - In-memory data store
  - Connection: Environment-configured
  - Usage: Caching, session storage, queue management
- Upstash Redis 1.3.0 - Serverless Redis
  - Purpose: Edge-compatible Redis alternative

**File Storage:**
- Supabase Storage - Object storage via Supabase client
  - Integration: Same credentials as database

## Authentication & Identity

**Auth Provider:**
- Supabase Auth - Managed authentication service
  - Implementation: JWT-based with cookie storage
  - Methods: Email/password, OAuth (Google, GitHub detected in code)
  - Frontend: `@supabase/ssr` for server-side rendering
  - MFA: Phone number verification via `libphonenumber-js` 1.12.10
  - SSO: `fastapi-sso` 0.9.0+ for backend OAuth flows

## Monitoring & Observability

**Error Tracking:**
- Sentry (referenced but optional)
  - Config: `NEXT_PUBLIC_SENTRY_DSN` environment variable
  - Implementation: Optional integration

**Logs:**
- structlog 25.4.0 - Structured logging (backend)
  - Format: JSON-structured logs
- AWS CloudWatch - Log aggregation
  - SDK: `watchtower` 3.0.0
  - Purpose: Centralized logging

**Analytics:**
- PostHog - Product analytics and feature flags
  - Client: `posthog-js` 1.258.6 (frontend), `posthog-node` 5.6.0 (backend)
  - Config: `NEXT_PUBLIC_POSTHOG_KEY`, `NEXT_PUBLIC_POSTHOG_HOST` (default: https://eu.i.posthog.com)
  - Safe wrapper: Custom initialization in `src/lib/posthog.ts`
- Google Tag Manager - Marketing analytics
  - Config: `NEXT_PUBLIC_GTM_ID`
  - Integration: `@next/third-parties` 15.3.1
- Google Analytics - Web analytics
  - SDK: `google-analytics-data` 0.18.0+
  - Purpose: Analytics data access

**Observability:**
- Langfuse 2.60.5 - LLM observability platform
  - Purpose: Trace LLM calls, monitor costs, debug AI agents
  - Connection: `cloud.langfuse.com` in CSP
- Prometheus - Metrics collection
  - Client: `prometheus-client` 0.21.1
  - Purpose: System metrics export
- Braintrust 0.3.15+ - AI evaluation
  - SDK: `braintrust`, `autoevals` 0.0.130
  - Purpose: LLM output evaluation

## CI/CD & Deployment

**Hosting:**
- Vercel (indicated by `@vercel/*` packages)
  - Packages: `@vercel/analytics` 1.5.0, `@vercel/speed-insights` 1.2.0, `@vercel/edge-config` 1.4.0
  - Platform: Edge Functions, serverless deployment

**CI Pipeline:**
- GitHub Actions (likely, based on typical Next.js/Vercel workflow)
  - Deployment: Automated via Vercel integration

**Containerization:**
- Docker - Backend containerization
  - Files: `Dockerfile`, `Dockerfile.production`, `Dockerfile.simple`
  - Base: `python:3.11-slim`
  - Server: Gunicorn + uvicorn workers

## Environment Configuration

**Required env vars:**
- **Database:** `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- **Backend:** `NEXT_PUBLIC_BACKEND_URL`, `INTERNAL_BACKEND_URL`, `BACKEND_URL`
- **Payment:** `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`, Stripe secret key (backend)
- **Analytics:** `NEXT_PUBLIC_POSTHOG_KEY`, `NEXT_PUBLIC_GTM_ID`
- **Notifications:** `NEXT_PUBLIC_NOVU_APP_IDENTIFIER`
- **Features:** `NEXT_PUBLIC_DISABLE_MOBILE_ADVERTISING`, `NEXT_PUBLIC_ENV_MODE`, `NEXT_PUBLIC_PHONE_NUMBER_MANDATORY`
- **Monitoring:** `NEXT_PUBLIC_SENTRY_DSN` (optional), `NEXT_PUBLIC_VERBOSE_LOGGING`
- **Misc:** `ORSHOT_API_KEY`, `NEXT_PUBLIC_URL`, `NEXT_PUBLIC_APP_URL`

**Secrets location:**
- Environment variables (not committed to git)
- Vercel environment variables (for deployment)

## Webhooks & Callbacks

**Incoming:**
- `/api/integrations/[provider]/callback` - OAuth callbacks
- `/api/triggers/[triggerId]/webhook` - Trigger webhooks
- Stripe webhooks (likely, given integration)

**Outgoing:**
- Backend API calls to external services
- E2B sandbox execution
- Composio tool integrations
- Tavily search requests

## Payment Processing

**Stripe:**
- Frontend: `@stripe/stripe-js` 8.6.4, `@stripe/react-stripe-js` 5.5.0
  - Config: `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`
  - Provider: `src/components/billing/stripe-provider.tsx`
- Backend: `stripe` 11.6.0
  - Purpose: Payment processing, subscription management

## Notification Systems

**Novu:**
- Frontend: `@novu/nextjs` 3.11.0, `@novu/notification-center` 2.0.0
  - Config: `NEXT_PUBLIC_NOVU_APP_IDENTIFIER`
  - Purpose: In-app notifications
- Backend: `novu-py` 3.11.0+
  - Purpose: Notification triggers

**Email:**
- Mailtrap 2.0.1 - Email testing/delivery
  - Purpose: Transactional emails
- `email-validator` 2.0.0 - Email validation

## Calendar Integration

**Cal.com:**
- Frontend: `@calcom/embed-react` 1.5.2
  - Purpose: Embedded calendar scheduling

## Security & Validation

**Tools:**
- `email-validator` 2.0.0 - Email format validation
- `phonenumbers` 8.13.50 - Phone number validation
- `cryptography` 41.0.0+ - Encryption primitives
- `pyjwt` 2.10.1 - JWT handling
- `certifi` 2025.4.26+ - SSL certificate validation

**Content Security:**
- `dompurify` 3.3.3 - HTML sanitization
- `isomorphic-dompurify` 2.19.0 - Universal sanitization
- Next.js CSP headers in `next.config.ts`

## Cloud Services

**AWS:**
- boto3 1.40.74+ - AWS SDK
  - Purpose: AWS service integration (S3, CloudWatch, etc.)

**Google Cloud:**
- `google-api-python-client` 2.120.0+ - Google APIs
- `google-auth` 2.28.0+ - Google authentication
- `google-auth-oauthlib` 1.2.0+ - OAuth flows
- Purpose: Google Workspace integrations

## Document Processing

**AI Document Processing:**
- Chunkr AI 0.3.7+ - Document chunking and parsing
  - Purpose: Intelligent document processing

**Libraries:**
- PyPDF2 3.0.1 - PDF reading
- python-docx 1.1.0 - Word document processing
- openpyxl 3.1.2 - Excel file handling
- python-pptx 1.0.0+ - PowerPoint processing
- beautifulsoup4 4.12.0+ - HTML parsing
- WeasyPrint 63.0+ - HTML to PDF conversion

## Specialized Integrations

**LCA & Knowledge Graph:**
- qdrant-client 1.11.0+ - Vector database
- fastembed 0.3.0+ - Fast embeddings
- langchain-openai 0.2.0+, langchain-anthropic 0.2.0+ - LangChain integrations
- langgraph 0.2.0+ - Graph-based workflows
- rdflib 7.0.0+ - RDF triple store
- SPARQLWrapper 2.0.0+ - SPARQL query interface
- owlready2 0.46+ - OWL ontology management
- graphrag-sdk 0.4.0+ - Graph retrieval-augmented generation

**Environmental Data:**
- brightway2 <2.5.0 - Life cycle assessment framework
  - Purpose: Carbon/environmental impact calculations

---

*Integration audit: 2026-04-06*
