#!/bin/bash

################################################################################
# CarbonScope Free Tier Deployment
# Deploy to Vercel (Frontend) + Railway (Backend) + Neon (Database)
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

clear
echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     CarbonScope Free Tier Deployment                          ║"
echo "║     Vercel + Railway + Neon + Upstash                         ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

print_info "This script will deploy CarbonScope using free tier services:"
echo "  • Vercel (Frontend) - Free forever"
echo "  • Railway (Backend) - \$5/month free credit"
echo "  • Neon (Database) - Free 3 GB"
echo "  • Upstash (Redis) - Free 10k commands/day"
echo ""
echo "  Total Cost: \$0/month"
echo "  Total Time: ~20 minutes"
echo ""

read -p "$(echo -e ${YELLOW}Continue with deployment? [y/N]: ${NC})" -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Deployment cancelled"
    exit 0
fi

# Check prerequisites
print_header "Checking Prerequisites"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js not found. Install: https://nodejs.org"
    exit 1
fi
print_success "Node.js installed: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    print_error "npm not found"
    exit 1
fi
print_success "npm installed: $(npm --version)"

# Install Vercel CLI
print_header "Installing Vercel CLI"

if ! command -v vercel &> /dev/null; then
    print_info "Installing Vercel CLI..."
    npm install -g vercel
    print_success "Vercel CLI installed"
else
    print_success "Vercel CLI already installed"
fi

# Install Railway CLI
print_header "Installing Railway CLI"

if ! command -v railway &> /dev/null; then
    print_info "Installing Railway CLI..."
    npm install -g @railway/cli
    print_success "Railway CLI installed"
else
    print_success "Railway CLI already installed"
fi

# Deploy Frontend to Vercel
print_header "Deploying Frontend to Vercel"

cd apps/frontend

print_info "Logging into Vercel..."
vercel login

print_info "Deploying to Vercel (this may take a few minutes)..."
VERCEL_URL=$(vercel --prod --yes 2>&1 | grep -o 'https://[^[:space:]]*' | head -1)

if [ -n "$VERCEL_URL" ]; then
    print_success "Frontend deployed: $VERCEL_URL"
else
    print_warning "Could not auto-detect URL. Check Vercel dashboard."
    VERCEL_URL="https://carbonscope.vercel.app"
fi

cd ../..

# Database Setup Instructions
print_header "Database Setup (Manual Step)"

echo ""
print_info "Create a Neon PostgreSQL database:"
echo ""
echo "1. Visit: https://console.neon.tech"
echo "2. Sign up with GitHub/Google"
echo "3. Create new project: 'CarbonScope'"
echo "4. Copy connection string"
echo ""

read -p "$(echo -e ${BLUE}Enter Neon DATABASE_URL: ${NC})" DATABASE_URL

if [ -z "$DATABASE_URL" ]; then
    print_error "DATABASE_URL required"
    exit 1
fi

print_success "Database URL saved"

# Redis Setup Instructions
print_header "Redis Setup (Manual Step)"

echo ""
print_info "Create an Upstash Redis database:"
echo ""
echo "1. Visit: https://console.upstash.com"
echo "2. Sign up"
echo "3. Create database: 'carbonscope'"
echo "4. Region: US-East-1"
echo "5. Copy Redis URL"
echo ""

read -p "$(echo -e ${BLUE}Enter Upstash REDIS_URL: ${NC})" REDIS_URL

if [ -z "$REDIS_URL" ]; then
    print_warning "REDIS_URL not provided (optional)"
    REDIS_URL=""
fi

# Deploy Backend to Railway
print_header "Deploying Backend to Railway"

cd backend

print_info "Logging into Railway..."
railway login

print_info "Initializing Railway project..."
railway init

print_info "Deploying to Railway..."
railway up

print_info "Setting environment variables..."
railway variables set DATABASE_URL="$DATABASE_URL"

if [ -n "$REDIS_URL" ]; then
    railway variables set REDIS_URL="$REDIS_URL"
fi

# Get Railway URL
RAILWAY_URL=$(railway status | grep -o 'https://[^[:space:]]*' | head -1)

if [ -n "$RAILWAY_URL" ]; then
    print_success "Backend deployed: $RAILWAY_URL"
else
    print_warning "Could not auto-detect Railway URL. Check dashboard."
    RAILWAY_URL="https://carbonscope-production.railway.app"
fi

cd ..

# Configure Vercel Environment Variables
print_header "Configuring Vercel Environment Variables"

cd apps/frontend

print_info "Getting NEXTAUTH_SECRET from .env.local..."
NEXTAUTH_SECRET=$(grep NEXTAUTH_SECRET .env.local | cut -d '=' -f2 | tr -d '"')

print_info "Setting Vercel environment variables..."

# Set NEXTAUTH_SECRET
echo "$NEXTAUTH_SECRET" | vercel env add NEXTAUTH_SECRET production

# Set DATABASE_URL
echo "$DATABASE_URL" | vercel env add DATABASE_URL production

# Set NEXT_PUBLIC_API_URL
echo "$RAILWAY_URL" | vercel env add NEXT_PUBLIC_API_URL production

# Set NEXTAUTH_URL
echo "$VERCEL_URL" | vercel env add NEXTAUTH_URL production

print_success "Environment variables configured"

# Get OAuth credentials
print_header "OAuth Configuration (Optional)"

echo ""
print_info "Do you want to configure OAuth now?"
echo "  You can skip and add later in Vercel dashboard"
echo ""

read -p "$(echo -e ${BLUE}Configure OAuth? [y/N]: ${NC})" -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Google OAuth
    echo ""
    print_info "Google OAuth Setup:"
    echo "  1. Visit: https://console.cloud.google.com/apis/credentials"
    echo "  2. Create OAuth 2.0 Client ID"
    echo "  3. Add redirect URI: $VERCEL_URL/api/auth/callback/google"
    echo ""
    read -p "$(echo -e ${BLUE}Enter Google Client ID: ${NC})" GOOGLE_CLIENT_ID
    read -p "$(echo -e ${BLUE}Enter Google Client Secret: ${NC})" GOOGLE_CLIENT_SECRET
    
    if [ -n "$GOOGLE_CLIENT_ID" ]; then
        echo "$GOOGLE_CLIENT_ID" | vercel env add GOOGLE_CLIENT_ID production
        echo "$GOOGLE_CLIENT_SECRET" | vercel env add GOOGLE_CLIENT_SECRET production
        print_success "Google OAuth configured"
    fi
    
    # GitHub OAuth
    echo ""
    print_info "GitHub OAuth Setup:"
    echo "  1. Visit: https://github.com/settings/developers"
    echo "  2. Create new OAuth App"
    echo "  3. Callback URL: $VERCEL_URL/api/auth/callback/github"
    echo ""
    read -p "$(echo -e ${BLUE}Enter GitHub Client ID: ${NC})" GITHUB_CLIENT_ID
    read -p "$(echo -e ${BLUE}Enter GitHub Client Secret: ${NC})" GITHUB_CLIENT_SECRET
    
    if [ -n "$GITHUB_CLIENT_ID" ]; then
        echo "$GITHUB_CLIENT_ID" | vercel env add GITHUB_CLIENT_ID production
        echo "$GITHUB_CLIENT_SECRET" | vercel env add GITHUB_CLIENT_SECRET production
        print_success "GitHub OAuth configured"
    fi
fi

# Run Prisma migrations
print_header "Running Database Migrations"

print_info "Running Prisma migrations..."
DATABASE_URL="$DATABASE_URL" npx prisma migrate deploy

print_info "Generating Prisma client..."
npx prisma generate

print_success "Database migrations complete"

# Redeploy frontend
print_header "Redeploying Frontend"

print_info "Redeploying to apply environment variables..."
vercel --prod --yes

print_success "Frontend redeployed"

cd ../..

# Summary
print_header "Deployment Complete!"

echo ""
echo -e "${GREEN}✓ CarbonScope successfully deployed!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "DEPLOYMENT URLS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${BLUE}Frontend:${NC}"
echo "  $VERCEL_URL"
echo ""
echo -e "${BLUE}Backend API:${NC}"
echo "  $RAILWAY_URL"
echo "  $RAILWAY_URL/docs (API documentation)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "NEXT STEPS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Test your application:"
echo "   Visit: $VERCEL_URL"
echo ""
echo "2. Test API:"
echo "   Visit: $RAILWAY_URL/docs"
echo ""
echo "3. Configure OAuth (if skipped):"
echo "   - Vercel Dashboard: https://vercel.com/dashboard"
echo "   - Settings → Environment Variables"
echo ""
echo "4. Add custom domain (optional):"
echo "   - Vercel Dashboard → Settings → Domains"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "COST"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  Vercel (Frontend):  \$0/month"
echo "  Railway (Backend):  \$0/month (\$5 credit)"
echo "  Neon (Database):    \$0/month"
echo "  Upstash (Redis):    \$0/month"
echo "  ────────────────────────────────"
echo "  Total:              \$0/month"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

print_success "Deployment complete! 🎉"
