# Technology Stack

**Analysis Date:** 2026-04-09

## Languages

**Primary:**
- Python 3.11+ - Backend services, AI agents, LCA calculations
- TypeScript 5.x - Frontend (Next.js), Mobile (React Native), Desktop (Electron), Shared packages

**Secondary:**
- Bash/Shell - DevOps scripts, deployment automation
- SQL - Database queries via Supabase/PostgreSQL

## Runtime

**Environment:**
- Python 3.11 (backend)
- Node.js (frontend/mobile/desktop - versions vary by platform)

**Package Manager:**
- pnpm (primary for monorepo)
- uv (Python package management, referenced in docs)
- pip (fallback for Python packages)

## Frameworks

**Core:**
- FastAPI 0.115.12 - Backend API framework
- Next.js 15.3.8 - Frontend web application (App Router)
- React Native 0.81.5 - Mobile application
- Electron 33.0.0 - Desktop application
- LangGraph 0.2.0 - Agent orchestration and state management
- LangChain - LLM integrations (openai, anthropic)

**Testing:**
- pytest 8.3.4 - Backend testing framework
- Playwright 1.59.1 - Frontend E2E testing
- Jest/Vitest - Implied via React Native testing setup

**Build/Dev:**
- Turbopack - Next.js compilation (optional)
- Webpack - Metro bundler for React Native
- Electron Builder - Desktop application packaging
- Tailwind CSS v4 - Styling framework
- PostCSS 8.4.33 - CSS processing
- ESLint 9.x - Linting
- Prettier 3.5.3 - Code formatting
- TypeScript - Type checking

## Key Dependencies

**Critical:**
- Supabase 2.17.0 - PostgreSQL database, auth, storage
- Redis 5.2.1 - Caching, session management, SSE fan-out via StreamHub
- LiteLLM >=1.80.11 - Unified LLM API interface (OpenAI, Anthropic, Azure, etc.)
- LangGraph-checkpoint-postgres>=2.0.0 - Agent state persistence
- Brightway2<2.5.0 - LCA (Life Cycle Assessment) calculations
- Qdrant-client>=1.11.0 - Vector database for embeddings
- Structlog==25.4.0 - Structured logging
- Novu-py>=3.11.0 - Notification infrastructure
- Zod^3.25.76 - Schema validation (shared TS package)

**Infrastructure:**
- Upstash-Redis==1.3.0 - Redis compatibility layer
- Boto3>=1.40.74 - AWS S3 integration
- Python-multipart==0.0.20 - File upload handling
- FastAPI-SSO>=0.9.0 - Authentication extensions
- Slowapi>=0.1.9 - Rate limiting
- Psycopg[binary]>=3.3.2 - PostgreSQL adapter
- SQLAlchemy>=2.0.45 - ORM
- Gunicorn>=23.0.0 - Production WSGI server
- Watchtower>=3.0.0 - CloudWatch Logs handler
- Composio>=0.8.0 - Tool integrations

## Configuration

**Environment:**
- Configured via .env files (backend/.env, apps/frontend/.env.local, etc.)
- Key variables: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, DATABASE_URL, REDIS_HOST/PORT/PASSWORD
- LLM API keys: ANTHROPIC_API_KEY, OPENAI_API_KEY, AWS_BEARER_TOKEN_BEDROCK
- Configuration loaded via pydantic-settings pattern in core/utils/config.py

**Build:**
- Backend: pyproject.toml with Poetry/uv dependencies
- Frontend: package.json with Next.js, Tailwind, Radix UI
- Mobile: package.json with Expo, React Native, NativeWind
- Desktop: package.json with Electron, Electron-builder
- Shared: package.json with TypeScript utilities

## Platform Requirements

**Development:**
- Python 3.11+
- Node.js 20.x (frontend), 18.x (mobile per overrides)
- pnpm package manager
- Docker (optional for containerized deployment)
- Git

**Production:**
- Linux-based containers (Docker/Kubernetes)
- Supabase PostgreSQL backend
- Redis instance
- Supported LLM provider APIs (OpenAI, Anthropic, Azure, etc.)
- HTTPS termination (via reverse proxy or platform)

---

*Stack analysis: 2026-04-09*