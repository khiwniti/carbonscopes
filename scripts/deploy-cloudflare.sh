#!/bin/bash
# Cloudflare Deployment Script
# Usage: ./scripts/deploy-cloudflare.sh [frontend|backend|all]

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if CLOUDFLARE_API_TOKEN is set
if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo -e "${RED}Error: CLOUDFLARE_API_TOKEN environment variable is not set${NC}"
    echo "Please set it with: export CLOUDFLARE_API_TOKEN=your_token"
    exit 1
fi

if [ -z "$CLOUDFLARE_ACCOUNT_ID" ]; then
    echo -e "${RED}Error: CLOUDFLARE_ACCOUNT_ID environment variable is not set${NC}"
    echo "Please set it with: export CLOUDFLARE_ACCOUNT_ID=your_account_id"
    exit 1
fi

DEPLOY_TARGET=${1:-all}

echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}  CarbonScope Cloudflare Deployment${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""
echo -e "Account ID: ${YELLOW}$CLOUDFLARE_ACCOUNT_ID${NC}"
echo -e "Target: ${YELLOW}$DEPLOY_TARGET${NC}"
echo ""

deploy_frontend() {
    echo -e "${BLUE}Deploying Frontend to Cloudflare Pages...${NC}"
    cd apps/frontend
    
    echo "Installing dependencies..."
    pnpm install --frozen-lockfile
    
    echo "Building Next.js for Cloudflare Pages..."
    pnpm pages:build
    
    echo "Deploying to Cloudflare Pages..."
    npx wrangler pages deploy .vercel/output/static --project-name=carbonscope-frontend --branch=main
    
    echo -e "${GREEN}Frontend deployed successfully!${NC}"
    cd ../..
}

deploy_backend() {
    echo -e "${BLUE}Deploying Backend to Cloudflare Containers...${NC}"
    cd backend
    
    echo "Installing Worker dependencies..."
    npm install
    
    echo "Deploying Container..."
    npx wrangler deploy --config wrangler.toml
    
    echo -e "${GREEN}Backend deployed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Note: Container provisioning takes a few minutes.${NC}"
    echo -e "${YELLOW}Run 'npx wrangler containers list' to check status.${NC}"
    cd ..
}

case $DEPLOY_TARGET in
    frontend)
        deploy_frontend
        ;;
    backend)
        deploy_backend
        ;;
    all)
        deploy_backend
        echo ""
        deploy_frontend
        ;;
    *)
        echo -e "${RED}Unknown target: $DEPLOY_TARGET${NC}"
        echo "Usage: $0 [frontend|backend|all]"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Deployment Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
