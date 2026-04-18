# Deployment Guide

## Overview

CarbonScopes uses a **Docker-based deployment** with separate containers for frontend and backend.

## Frontend (Next.js)

### Docker Build (Recommended)

Build from monorepo root:

```bash
docker build -f apps/frontend/Dockerfile \
  --build-arg NEXT_PUBLIC_SUPABASE_URL=$NEXT_PUBLIC_SUPABASE_URL \
  --build-arg NEXT_PUBLIC_SUPABASE_ANON_KEY=$NEXT_PUBLIC_SUPABASE_ANON_KEY \
  --build-arg NEXT_PUBLIC_BACKEND_URL=$NEXT_PUBLIC_BACKEND_URL \
  -t carbonscope-frontend:latest .
```

Run:
```bash
docker run -p 3000:3000 carbonscope-frontend:latest
```

### Build Requirements

| Requirement | Value |
|-------------|-------|
| **Memory** | 4GB heap required (`NODE_OPTIONS='--max-old-space-size=4096'`)|
| **Node** | 20.x |
| **pnpm** | 10.x |
| **Build time** | 5-10 minutes |

**Why 4GB?** The Next.js build requires significant memory due to:
- Large dependency tree (TipTap, Radix UI, SyncFusion, etc.)
- TypeScript compilation across monorepo packages
- Standalone output generation for production

### Cloudflare Pages (Alternative)

For edge deployment:

```bash
cd apps/frontend
pnpm run pages:build
pnpm run pages:deploy
```

## Backend (Python/FastAPI)

### Using uv (Recommended for Development)

```bash
cd backend
uv sync
uv run uvicorn api:app --host 0.0.0.0 --port 8000
```

### Using Docker (Recommended for Production)

```bash
cd backend
docker build -t carbonscope-backend:latest .
docker run -p 8000:8000 --env-file .env carbonscope-backend:latest
```

## Environment Variables

### Frontend (Build-time)

These are embedded at build time and cannot change at runtime:

```bash
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_BACKEND_URL=https://api.your-domain.com/v1
```

### Backend (Runtime)

```bash
DATABASE_URL=postgresql://user:pass@host/db
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-key
NEXTAUTH_SECRET=your-nextauth-secret
```

## CI/CD Integration

GitHub Actions automatically runs on every push:
- Frontend: lint, type-check, build (with 4GB heap)
- Backend: ruff lint, pytest
- Security: TruffleHog secret scanning

See `.github/workflows/ci.yml` for details.

## Troubleshooting

### Build fails with memory error
Ensure `NODE_OPTIONS='--max-old-space-size=4096'` is set:
```bash
export NODE_OPTIONS='--max-old-space-size=4096'
pnpm run build
```

### Docker build fails on monorepo packages
The Dockerfile handles `@agentpress/shared` by:
1. Copying the package source
2. Compiling TypeScript to JavaScript
3. Updating package.json exports to point to `dist/`

### Backend tests fail
Ensure test database is configured:
```bash
cd backend
pytest tests/ -x -v
```
