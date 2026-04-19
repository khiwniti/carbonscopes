# Cloudflare Deployment Guide

This guide covers deploying both the CarbonScope frontend and backend to Cloudflare.

## Architecture

- **Frontend**: Deployed to Cloudflare Pages using `@cloudflare/next-on-pages`
- **Backend**: Deployed to Cloudflare Containers with a Worker as the entry point

## Prerequisites

1. Cloudflare account with access to:
   - Cloudflare Pages
   - Cloudflare Containers (beta)
   - Workers

2. API Token with permissions:
   - Cloudflare Pages: Edit
   - Workers Scripts: Edit
   - Account Settings: Read
   - Container Registry: Edit (for Cloudflare Containers)

## Setup Instructions

### 1. Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings → Secrets and variables → Actions):

| Secret | Description |
|--------|-------------|
| `CLOUDFLARE_API_TOKEN` | Your Cloudflare API token (from https://dash.cloudflare.com/profile/api-tokens) |
| `CLOUDFLARE_ACCOUNT_ID` | Your Cloudflare Account ID (from dashboard sidebar) |
| `NEXT_PUBLIC_API_URL` | URL of your deployed backend (set after first backend deploy) |

### 2. Create Cloudflare API Token

1. Go to https://dash.cloudflare.com/profile/api-tokens
2. Click "Create Token"
3. Use the "Custom token" template
4. Configure permissions:
   - **Account**: Cloudflare Pages:Edit
   - **Account**: Workers Scripts:Edit
   - **Account**: Account Settings:Read
   - **Zone**: (if using custom domain)
5. Include your account and zone resources
6. Create token and copy to GitHub secrets

### 3. Deploy Backend Secrets

The backend requires secrets to be set via Wrangler:

```bash
cd backend
# Login to Cloudflare
npx wrangler login

# Set required secrets
npx wrangler secret put SUPABASE_URL
npx wrangler secret put SUPABASE_SERVICE_KEY
npx wrangler secret put SUPABASE_ANON_KEY
npx wrangler secret put REDIS_URL
npx wrangler secret put JWT_SECRET
npx wrangler secret put OPENAI_API_KEY

# Add any other secrets from your .env file
```

### 4. Local Testing

**Frontend:**
```bash
cd apps/frontend
pnpm pages:dev
```

**Backend Container:**
```bash
cd backend
# Build and test locally
docker build -t carbonscope-backend .
docker run -p 8000:8000 --env-file .env carbonscope-backend
```

### 5. Manual Deployment

If you want to deploy manually instead of via GitHub Actions:

**Frontend:**
```bash
cd apps/frontend
pnpm pages:build
npx wrangler pages deploy .vercel/output/static --project-name=carbonscope-frontend
```

**Backend:**
```bash
cd backend
npm install
npx wrangler deploy
```

## Configuration Files

### Frontend (`apps/frontend/wrangler.toml`)
```toml
name = "carbonscopes-frontend"
compatibility_date = "2025-04-01"
compatibility_flags = ["nodejs_compat"]
pages_build_output_dir = ".vercel/output/static"
```

### Backend (`backend/wrangler.toml`)
```toml
name = "carbonscope-backend"
main = "index.js"
compatibility_date = "2025-04-19"

[[containers]]
name = "backend"
class_name = "CarbonScopeBackend"
image = "./Dockerfile"
max_instances = 5
instance_type = "medium"
```

## Troubleshooting

### Container deployment fails
- Ensure Docker is running locally
- Check that your Dockerfile builds successfully: `docker build .`
- Verify your Cloudflare account has Containers access enabled

### Pages deployment fails
- Check that `pnpm pages:build` succeeds locally
- Verify `.vercel/output/static` is generated

### Secrets not available
- Secrets must be set via `wrangler secret put` or Cloudflare dashboard
- Environment variables in `wrangler.toml` [vars] section are not secrets

## Instance Types

Cloudflare Containers support these instance types:

| Type | vCPU | Memory | Disk |
|------|------|--------|------|
| nano | 0.0625 | 128 MiB | 2 GB |
| micro | 0.125 | 256 MiB | 2 GB |
| small | 0.25 | 512 MiB | 2 GB |
| medium | 0.5 | 512 MiB | 2 GB |
| large | 1 | 1024 MiB | 4 GB |
| xl | 2 | 2048 MiB | 4 GB |

Or use custom configuration:
```toml
[containers.instance_type]
vcpu = 1
memory_mib = 1024
disk_mb = 4000
```

## Resources

- [Cloudflare Containers Docs](https://developers.cloudflare.com/containers/)
- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)
- [Wrangler Configuration](https://developers.cloudflare.com/workers/wrangler/configuration/)
