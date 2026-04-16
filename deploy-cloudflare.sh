#!/bin/bash
# ===========================================
# Cloudflare Deployment Script for CarbonScope
# ===========================================
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}  CarbonScope Cloudflare Deployment${NC}"
echo -e "${GREEN}===========================================${NC}"

# Check prerequisites
echo -e "\n${YELLOW}[1/5] Checking prerequisites...${NC}"

if ! command -v wrangler &> /dev/null; then
    echo -e "${RED}Wrangler CLI not found. Installing...${NC}"
    npm install -g wrangler
fi

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker not found. Please install Docker first.${NC}"
    exit 1
fi

# Login to Cloudflare
echo -e "\n${YELLOW}[2/5] Logging in to Cloudflare...${NC}"
wrangler login

# ===========================================
# BACKEND DEPLOYMENT
# ===========================================
echo -e "\n${YELLOW}[3/5] Deploying Backend to Cloudflare Container...${NC}"

echo "Enter your Docker image (e.g., ghcr.io/your-org/carbonscopes-backend:latest):"
read -r DOCKER_IMAGE

if [ -z "$DOCKER_IMAGE" ]; then
    echo -e "${RED}Docker image is required!${NC}"
    exit 1
fi

# Update wrangler.jsonc with the image
cd /workspace/project/carbonscopes/cloudflare-container
sed -i "s|ghcr.io/your-org/carbonscopes-backend:latest|$DOCKER_IMAGE|g" wrangler.jsonc

# Set required secrets
echo -e "\n${YELLOW}Setting up secrets (press Enter to skip optional ones):${NC}"

read -p "SUPABASE_URL [https://vplbjxijbrgwskgxiukd.supabase.co]: " SUPABASE_URL
SUPABASE_URL=${SUPABASE_URL:-https://vplbjxijbrgwskgxiukd.supabase.co}

read -p "SUPABASE_SERVICE_KEY: " SUPABASE_SERVICE_KEY
if [ -z "$SUPABASE_SERVICE_KEY" ]; then
    echo -e "${RED}SUPABASE_SERVICE_KEY is required!${NC}"
    exit 1
fi

read -p "SUPABASE_ANON_KEY: " SUPABASE_ANON_KEY
if [ -z "$SUPABASE_ANON_KEY" ]; then
    echo -e "${RED}SUPABASE_ANON_KEY is required!${NC}"
    exit 1
fi

read -p "UPSTASH_REDIS_REST_URL: " UPSTASH_REDIS_REST_URL
read -p "UPSTASH_REDIS_REST_TOKEN: " UPSTASH_REDIS_REST_TOKEN
read -p "OPENAI_API_KEY: " OPENAI_API_KEY
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}OPENAI_API_KEY is optional but recommended${NC}"
fi

read -p "ANTHROPIC_API_KEY: " ANTHROPIC_API_KEY
read -p "JWT_SECRET (or press Enter to generate): " JWT_SECRET
if [ -z "$JWT_SECRET" ]; then
    JWT_SECRET=$(openssl rand -base64 32)
    echo "Generated JWT_SECRET: $JWT_SECRET"
fi

# Set secrets
echo -e "\n${YELLOW}Setting Cloudflare secrets...${NC}"
echo $SUPABASE_URL | wrangler secret put SUPABASE_URL
echo $SUPABASE_SERVICE_KEY | wrangler secret put SUPABASE_SERVICE_KEY
echo $SUPABASE_ANON_KEY | wrangler secret put SUPABASE_ANON_KEY

if [ -n "$UPSTASH_REDIS_REST_URL" ]; then
    echo $UPSTASH_REDIS_REST_URL | wrangler secret put UPSTASH_REDIS_REST_URL
fi
if [ -n "$UPSTASH_REDIS_REST_TOKEN" ]; then
    echo $UPSTASH_REDIS_REST_TOKEN | wrangler secret put UPSTASH_REDIS_REST_TOKEN
fi
if [ -n "$OPENAI_API_KEY" ]; then
    echo $OPENAI_API_KEY | wrangler secret put OPENAI_API_KEY
fi
if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo $ANTHROPIC_API_KEY | wrangler secret put ANTHROPIC_API_KEY
fi
echo $JWT_SECRET | wrangler secret put JWT_SECRET

# Deploy backend
echo -e "\n${YELLOW}Deploying backend container...${NC}"
wrangler deploy

echo -e "${GREEN}Backend deployed!${NC}"
echo "Note the backend URL for the frontend configuration."

# ===========================================
# FRONTEND DEPLOYMENT
# ===========================================
echo -e "\n${YELLOW}[4/5] Deploying Frontend to Cloudflare Pages...${NC}"

cd /workspace/project/carbonscopes/apps/frontend

echo "Enter backend URL (e.g., https://api.carbonscope.simu.space/v1):"
read -r BACKEND_URL
BACKEND_URL=${BACKEND_URL:-https://api.carbonscope.simu.space/v1}

# Update .env.production with correct backend URL
sed -i "s|NEXT_PUBLIC_BACKEND_URL=.*|NEXT_PUBLIC_BACKEND_URL=$BACKEND_URL|g" .env.production
sed -i "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=$BACKEND_URL|g" .env.production
sed -i "s|NEXT_PUBLIC_URL=.*|NEXT_PUBLIC_URL=https://carbonscope.simu.space|g" .env.production

# Build frontend
echo -e "\n${YELLOW}Building frontend...${NC}"
pnpm build

# Deploy to Cloudflare Pages
echo -e "\n${YELLOW}Deploying to Cloudflare Pages...${NC}"
wrangler pages project create carbonscope-frontend --production-branch main 2>/dev/null || true
wrangler pages deploy .next --project-name=carbonscope-frontend

# ===========================================
# FINAL STATUS
# ===========================================
echo -e "\n${YELLOW}[5/5] Deployment Complete!${NC}"

echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}  Deployment Summary${NC}"
echo -e "${GREEN}===========================================${NC}"
echo ""
echo "Frontend: https://carbonscope.simu.space"
echo "Backend:  $BACKEND_URL"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Configure custom domains in Cloudflare dashboard"
echo "2. Set up DNS records for carbonscope.simu.space"
echo "3. Enable anonymous sign-in in Supabase (optional)"
echo ""