# Technology Stack

**Analysis Date:** 2026-04-06

## Languages

**Primary:**
- TypeScript 5.x - Frontend (Next.js), shared packages
- Python 3.11+ - Backend API (requires >=3.11)

**Secondary:**
- JavaScript - Configuration files, build scripts

## Runtime

**Environment:**
- Node.js v25.2.1 (development environment detected)
- Python 3.14.3 (development environment detected)

**Package Manager:**
- pnpm 10.26.1
- Lockfile: `pnpm-lock.yaml` present

**Workspace:**
- pnpm workspaces with monorepo structure
- Workspaces: `apps/*`, `packages/*`

## Frameworks

**Core:**
- Next.js 15.3.8 - Frontend framework with App Router
- FastAPI 0.115.12 - Python backend API framework
- React 18/19 - UI library (frontend and mobile)
- React Native 0.81.5 - Mobile app framework
- Expo ~54.0.20 - React Native development platform
- Electron 33.0.0 - Desktop application wrapper

**Testing:**
- Playwright 1.59.1 - E2E browser testing
- pytest 8.3.4 - Python testing framework
- pytest-asyncio 0.24.0 - Async test support

**Build/Dev:**
- Turbopack - Next.js bundler (via `dev:turbo` script)
- uvicorn 0.27.1 - ASGI server for FastAPI
- Gunicorn 23.0.0+ - Production WSGI server
- electron-builder 25.1.8 - Desktop app packaging

## Key Dependencies

**Critical:**
- `@supabase/supabase-js` (latest) - Database client
- `@supabase/ssr` (latest) - Supabase Server-Side Rendering
- `@stripe/stripe-js` 8.6.4 - Payment processing client
- `@stripe/react-stripe-js` 5.5.0 - Stripe React integration
- `@tanstack/react-query` 5.75.2+ - Data fetching/caching
- zustand 5.0.3+ - State management

**Infrastructure:**
- Radix UI (multiple packages) - Headless UI components
- TailwindCSS 4.x - Utility-first CSS framework
- Tiptap 3.x - Rich text editor
- CodeMirror 6.x - Code editor
- Framer Motion 12.6.5 - Animation library
- PostHog (posthog-js, posthog-node) - Analytics
- Novu 3.11.0+ - Notification infrastructure

**Python Backend:**
- litellm 1.80.11+ - LLM provider abstraction
- Prisma 0.15.0 - Database ORM
- Anthropic 0.69.0+ - Claude API client
- OpenAI 1.99.5+ - OpenAI API client
- Stripe 11.6.0 - Payment processing
- Tavily 0.5.4 - Web search tool
- E2B Code Interpreter 1.2.0 - Sandbox execution
- Composio 0.8.0+ - Integration platform
- Langfuse 2.60.5 - LLM observability
- Redis 5.2.1 - Caching layer
- Upstash Redis 1.3.0 - Serverless Redis

## Configuration

**Environment:**
- Frontend env vars: `NEXT_PUBLIC_*` prefix for client-side
- Backend configured via environment variables
- No `.env` files detected (likely gitignored)

**Build:**
- `next.config.ts` - Next.js configuration with security headers
- `playwright.config.ts` - E2E test configuration
- `pyproject.toml` - Python project configuration
- `tsconfig.json` - TypeScript compiler settings
- Output mode: `standalone` for Next.js deployment

## Platform Requirements

**Development:**
- Node.js 18+ (using v25.2.1)
- Python 3.11+ (using 3.14.3)
- pnpm package manager
- Docker for containerized backend

**Production:**
- Next.js: Standalone output for containerization
- Backend: Docker container with Python 3.11-slim
- Gunicorn with 2+ workers (configurable)
- ASGI server (uvicorn) for async FastAPI
- Port 3000 (frontend), 8000 (backend)

---

*Stack analysis: 2026-04-06*
