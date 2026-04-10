# Technology Stack

**Analysis Date:** 2026-04-10

## Languages

**Primary:**
- TypeScript 5.x - Used throughout frontend applications (Next.js) and shared packages
- Python 3.11+ - Used for backend API services, agents, and infrastructure

**Secondary:**
- JavaScript ES2017 - Used in frontend with TypeScript transpilation
- SQL - Used for database queries and migrations

## Runtime

**Environment:**
- Node.js 20.x - Frontend and infrastructure runtime
- Python 3.11+ - Backend services runtime

**Package Manager:**
- pnpm - Used for frontend, shared packages, and infrastructure
- pip/uv - Used for backend Python dependencies (inferred from pyproject.toml and uv.lock presence)

## Frameworks

**Core:**
- Next.js 15.3.8 - React framework for frontend application
- FastAPI 0.115.12 - Python web framework for backend API
- React 18 - Frontend UI library
- Pulumi 3.113.0 - Infrastructure as Code framework

**Testing:**
- Playwright 1.59.1 - End-to-end testing framework
- pytest 8.3.4 - Python testing framework
- @tanstack/react-query - React state management for server state

**Build/Dev:**
- Turbopack - Next.js bundler (dev mode)
- Webpack - Bundling (production build)
- Tailwind CSS 4 - Utility-first CSS framework
- ESLint 9 - JavaScript/TypeScript linting
- Prettier 3.5.3 - Code formatting
- TypeScript 5 - Type checking

## Key Dependencies

**Critical:**
- @supabase/supabase-js - Database and authentication client
- stripe - Payment processing integration
- novu - Notification infrastructure
- langfuse - LLM observability and tracing
- redis/upstash-redis - Caching and session storage
- openai - LLM API integration
- anthropic - Claude LLM API integration
- prisma - ORM for database interactions
- langchain/openai/langchain-anthropic - LLM orchestration
- qdrant-client - Vector database for embeddings
- composio - Agent tooling framework
- mcp - Model Context Protocol implementation

**Infrastructure:**
- @pulumi/aws, @pulumi/awsx, @pulumi/kubernetes - Cloud infrastructure provisioning
- docker - Containerization
- gunicorn - Python WSGI HTTP server
- uvicorn - ASGI server for FastAPI

## Configuration

**Environment:**
- Configured via .env files (not committed) and .env.example templates
- Key configurations: SUPABASE_URL, SUPABASE_ANON_KEY, OPENAI_API_KEY, ANTHROPIC_API_KEY, STRIPE_KEY, etc.

**Build:**
- Frontend: next.config.ts, tailwind.config.ts, postcss.config.js
- Backend: pyproject.toml, alembic.ini (inferred)
- Infrastructure: Pulumi.yaml, TypeScript configuration

## Platform Requirements

**Development:**
- Node.js 20.x+
- Python 3.11+
- pnpm package manager
- Docker for containerized services
- Git for version control

**Production:**
- Deployment targets: AWS, Azure, Vercel (inferred from deployment scripts)
- Container orchestration: Docker Compose, Kubernetes (inferred from Pulumi configs)
- Database: Supabase PostgreSQL
- Redis for caching and session storage

---

*Stack analysis: 2026-04-10*