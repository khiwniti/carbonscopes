#!/bin/bash
# Setup Cloudflare Secrets for Backend
# Usage: ./scripts/setup-secrets.sh
# Requires: CLOUDFLARE_API_TOKEN and CLOUDFLARE_ACCOUNT_ID env vars

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

if [ -z "$CLOUDFLARE_API_TOKEN" ]; then
    echo -e "${RED}Error: CLOUDFLARE_API_TOKEN is not set${NC}"
    exit 1
fi

if [ -z "$CLOUDFLARE_ACCOUNT_ID" ]; then
    echo -e "${RED}Error: CLOUDFLARE_ACCOUNT_ID is not set${NC}"
    exit 1
fi

echo -e "${BLUE}Setting up Cloudflare secrets for CarbonScope Backend${NC}"
echo ""

cd backend

# List of required secrets
SECRETS=(
    "SUPABASE_URL"
    "SUPABASE_SERVICE_KEY"
    "SUPABASE_ANON_KEY"
    "REDIS_URL"
    "JWT_SECRET"
    "OPENAI_API_KEY"
)

echo -e "${YELLOW}The following secrets need to be configured:${NC}"
for secret in "${SECRETS[@]}"; do
    echo "  - $secret"
done

echo ""
echo -e "${BLUE}You can set secrets individually or import from .env file${NC}"
echo ""
echo "Options:"
echo "  1) Set secrets one by one (interactive)"
echo "  2) Import from backend/.env file"
echo "  3) Cancel"
echo ""
read -p "Select option (1-3): " choice

case $choice in
    1)
        for secret in "${SECRETS[@]}"; do
            echo ""
            read -p "Enter value for $secret (or press Enter to skip): " value
            if [ ! -z "$value" ]; then
                echo "$value" | npx wrangler secret put "$secret"
                echo -e "${GREEN}✓ Set $secret${NC}"
            else
                echo -e "${YELLOW}  Skipped $secret${NC}"
            fi
        done
        ;;
    2)
        if [ ! -f .env ]; then
            echo -e "${RED}Error: .env file not found in backend/ directory${NC}"
            exit 1
        fi
        
        echo -e "${BLUE}Importing secrets from .env file...${NC}"
        while IFS='=' read -r key value; do
            # Skip empty lines and comments
            [[ -z "$key" || "$key" =~ ^# ]] && continue
            
            # Remove quotes if present
            value=$(echo "$value" | sed -e 's/^["\'"'"']*//;s/["\'"'"']*$//')
            
            # Check if it's in our secrets list
            for secret in "${SECRETS[@]}"; do
                if [ "$key" == "$secret" ]; then
                    echo -e "Setting ${YELLOW}$key${NC}..."
                    echo "$value" | npx wrangler secret put "$key"
                    echo -e "${GREEN}✓ Set $key${NC}"
                    break
                fi
            done
        done < .env
        ;;
    3)
        echo "Cancelled."
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid option${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Secrets setup complete!${NC}"
echo ""
echo -e "${BLUE}You can verify secrets with:${NC}"
echo "  cd backend && npx wrangler secret list"
