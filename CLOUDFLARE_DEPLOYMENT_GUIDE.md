# Cloudflare Deployment Guide

This guide covers deploying CarbonScope to Cloudflare:
- **Frontend**: Cloudflare Pages
- **Backend**: Cloudflare Container (Workers for Platforms)

## Prerequisites

1. Cloudflare account with Workers & Pages enabled
2. Docker Hub or GHCR account for container images
3. Wrangler CLI installed: `npm install -g wrangler`
4. Supabase project (existing)

---

## Part 1: Backend Deployment (Cloudflare Container)

### Step 1: Prepare Backend Container Image

```bash
cd /workspace/project/carbonscopes/backend

# Build the Docker image
docker build -t carbonscopes-backend:latest .

# Push to Docker Hub or GHCR
# For Docker Hub:
docker tag carbonscopes-backend:latest your-dockerhub-user/carbonscopes-backend:latest
docker push your-dockerhub-user/carbonscopes-backend:latest

# For GHCR:
docker tag carbonscopes-backend:latest ghcr.io/your-org/carbonscopes-backend:latest
docker push ghcr.io/your-org/carbonscopes-backend:latest
```

### Step 2: Update wrangler.jsonc

Edit `/cloudflare-container/wrangler.jsonc` and update:
```jsonc
{
  "containers": [
    {
      "name": "backend",
      "image": "ghcr.io/your-org/carbonscopes-backend:latest",  // Update this
      ...
    }
  ]
}
```

### Step 3: Set Cloudflare Secrets

```bash
cd /workspace/project/carbonscopes/cloudflare-container

# Login to Cloudflare
wrangler login

# Set all required secrets
wrangler secret put SUPABASE_URL
wrangler secret put SUPABASE_SERVICE_KEY
wrangler secret put SUPABASE_ANON_KEY
wrangler secret put UPSTASH_REDIS_REST_URL
wrangler secret put UPSTASH_REDIS_REST_TOKEN
wrangler secret put OPENAI_API_KEY
wrangler secret put ANTHROPIC_API_KEY
wrangler secret put STRIPE_SECRET_KEY
wrangler secret put STRIPE_WEBHOOK_SECRET
wrangler secret put LANGFUSE_SECRET_KEY
wrangler secret put LANGFUSE_PUBLIC_KEY
wrangler secret put JWT_SECRET
```

### Step 4: Deploy Backend

```bash
cd /workspace/project/carbonscopes/cloudflare-container

# Deploy container
wrangler deploy

# Note the backend URL from output, e.g.:
# https://carbonscope-backend.accounts.cloudflare.workers.dev
```

---

## Part 2: Frontend Deployment (Cloudflare Pages)

### Step 1: Connect to Cloudflare Pages

Option A - Via Dashboard:
1. Go to https://pages.cloudflare.com
2. Click "Create a project"
3. Connect your GitHub repository
4. Configure build settings

Option B - Via Wrangler:
```bash
cd /workspace/project/carbonscopes/apps/frontend

# Initialize Pages project
wrangler pages project create carbonscope-frontend

# Deploy
wrangler pages deploy out/ --project-name=carbonscope-frontend
```

### Step 2: Frontend Environment Variables

Set in Cloudflare Pages dashboard → Settings → Environment Variables:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_ENV_MODE` | `production` |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://vplbjxijbrgwskgxiukd.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | (from Supabase dashboard) |
| `NEXT_PUBLIC_BACKEND_URL` | (your deployed backend URL from Part 1, e.g., `https://api.carbonscope.simu.space/v1`) |
| `NEXT_PUBLIC_URL` | `https://carbonscope.simu.space` |

### Step 3: Build Settings

- **Framework preset**: Next.js
- **Build command**: `pnpm build`
- **Build output directory**: `.next`
- **Root directory**: `apps/frontend`

---

## Part 3: Update CORS & Redirects

### Backend CORS (Update in your backend code)

```python
# Allow your Cloudflare Pages domain
CORS_ORIGINS = [
    "https://carbonscope-frontend.pages.dev",
    "https://carbonscope.your-domain.com",  # Custom domain
]
```

### Frontend next.config.ts

Update `/apps/frontend/next.config.ts`:
```typescript
connect-src 'self' 
  https://api.carbonscope.simu.space  // Backend URL
  https://vplbjxijbrgwskgxiukd.supabase.co 
  wss://vplbjxijbrgwskgxiukd.supabase.co
  ...
```

---

## Part 4: Custom Domain (Optional)

### Frontend (Cloudflare Pages)
1. Go to Pages → Your project → Custom domains
2. Add `carbonscope.your-domain.com`

### Backend (Cloudflare Container)
1. After deploy, go to Workers & Spaces → Your worker → Settings → Triggers
2. Add custom route `api.your-domain.com/*`

---

## Required Secrets Reference

### Supabase
- `SUPABASE_URL`: https://vplbjxijbrgwskgxiukd.supabase.co
- `SUPABASE_SERVICE_KEY`: Get from Supabase Dashboard → Settings → API
- `SUPABASE_ANON_KEY`: Get from Supabase Dashboard → Settings → API

### Redis (Upstash)
- `UPSTASH_REDIS_REST_URL`: From Upstash dashboard
- `UPSTASH_REDIS_REST_TOKEN`: From Upstash dashboard

### LLM APIs
- `OPENAI_API_KEY`: sk-... from OpenAI
- `ANTHROPIC_API_KEY`: sk-ant-... from Anthropic

### Stripe
- `STRIPE_SECRET_KEY`: sk_live_... from Stripe
- `STRIPE_WEBHOOK_SECRET`: whsec_... from Stripe webhook settings

### Analytics
- `LANGFUSE_SECRET_KEY`: sk-lf-... from Langfuse
- `LANGFUSE_PUBLIC_KEY`: pk-lf-... from Langfuse
- `LANGFUSE_HOST`: https://cloud.langfuse.com

### Other
- `JWT_SECRET`: Generate a secure random string
- `ENV_MODE`: production

---

## Quick Deploy Commands

```bash
# Backend
cd cloudflare-container
wrangler secret put <SECRET_NAME>  # Repeat for each secret
wrangler deploy

# Frontend
cd apps/frontend
pnpm build
wrangler pages deploy .next --project-name=carbonscope-frontend
```

---

## Troubleshooting

### Backend won't start
- Check logs: `wrangler tail`
- Verify all secrets are set
- Check container health: `curl https://your-backend.workers.dev/healthz`

### Frontend CORS errors
- Update `connect-src` in next.config.ts
- Add domain to backend CORS_ORIGINS

### Database connection issues
- Verify SUPABASE_URL and keys are correct
- Check Supabase SSL settings

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        Cloudflare                           │
│  ┌─────────────────────┐    ┌────────────────────────────┐  │
│  │   Cloudflare Pages  │    │  Cloudflare Container      │  │
│  │   (Frontend)        │    │  (Backend API)             │  │
│  │                     │    │                            │  │
│  │  carbonscope-       │    │  carbonscope-backend       │  │
│  │  frontend.pages.dev │────│  .workers.dev              │  │
│  └─────────────────────┘    └────────────────────────────┘  │
│                                      │                      │
└──────────────────────────────────────│──────────────────────┘
                                       │
                          ┌────────────┴───────────┐
                          │       Supabase         │
                          │   (Database/Auth)      │
                          └────────────────────────┘
```