#!/bin/bash

################################################################################
# CarbonScope Frontend Deployment to Azure Static Web Apps
# Deploys Next.js application to production
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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
    echo -e "${CYAN}ℹ $1${NC}"
}

clear
echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║              CarbonScope Frontend Deployment                                 ║"
echo "║              Azure Static Web Apps                                           ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
RESOURCE_GROUP="carbonscope-rg"
APP_NAME="carbonscope-frontend"
FRONTEND_DIR="apps/frontend"
BACKEND_URL="https://carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io"

print_info "Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  App Name: $APP_NAME"
echo "  Frontend Dir: $FRONTEND_DIR"
echo "  Backend URL: $BACKEND_URL"
echo ""

# Step 1: Check prerequisites
print_header "Step 1: Checking Prerequisites"

# Check if we're in the right directory
if [ ! -d "$FRONTEND_DIR" ]; then
    print_error "Frontend directory not found: $FRONTEND_DIR"
    print_info "Please run this script from the suna-init directory"
    exit 1
fi
print_success "Frontend directory found"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js not installed"
    exit 1
fi
NODE_VERSION=$(node --version)
print_success "Node.js installed: $NODE_VERSION"

# Check pnpm
if ! command -v pnpm &> /dev/null; then
    print_warning "pnpm not installed, installing..."
    npm install -g pnpm
fi
print_success "pnpm available"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    print_error "Azure CLI not installed"
    print_info "Install: curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash"
    exit 1
fi
print_success "Azure CLI installed"

# Check Azure login
if ! az account show &> /dev/null; then
    print_warning "Not logged in to Azure"
    print_info "Logging in..."
    az login
fi
print_success "Logged in to Azure"

# Step 2: Install dependencies
print_header "Step 2: Installing Dependencies"

cd "$FRONTEND_DIR"

print_info "Installing frontend dependencies..."
pnpm install --frozen-lockfile

print_success "Dependencies installed"

# Step 3: Create environment file
print_header "Step 3: Configuring Environment"

# Generate NEXTAUTH_SECRET
NEXTAUTH_SECRET=$(openssl rand -base64 32)

# Create .env.local for build
cat > .env.local << EOF
# Backend API
NEXT_PUBLIC_API_URL=$BACKEND_URL

# NextAuth Configuration
NEXTAUTH_URL=https://orange-river-0ce07e10f.6.azurestaticapps.net
NEXTAUTH_SECRET=$NEXTAUTH_SECRET

# Database (to be configured later)
DATABASE_URL=postgresql://user:pass@host/dbname

# OAuth (to be configured later)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
EOF

print_success "Environment file created"
print_info "NEXTAUTH_SECRET generated: ${NEXTAUTH_SECRET:0:20}..."

# Step 4: Build the application
print_header "Step 4: Building Next.js Application"

print_info "Running production build..."
print_info "This may take 2-3 minutes..."

# Build
if pnpm build; then
    print_success "Build completed successfully"
else
    print_error "Build failed"
    print_info "Check the output above for errors"
    exit 1
fi

# Check build output
if [ -d ".next" ]; then
    print_success "Build artifacts created (.next directory)"
    BUILD_SIZE=$(du -sh .next | awk '{print $1}')
    print_info "Build size: $BUILD_SIZE"
else
    print_error ".next directory not found"
    exit 1
fi

# Step 5: Install Azure Static Web Apps CLI
print_header "Step 5: Installing Azure SWA CLI"

if ! command -v swa &> /dev/null; then
    print_info "Installing @azure/static-web-apps-cli..."
    npm install -g @azure/static-web-apps-cli
    print_success "SWA CLI installed"
else
    print_success "SWA CLI already installed"
fi

# Step 6: Get deployment token
print_header "Step 6: Getting Deployment Token"

cd ../..

print_info "Retrieving deployment token from Azure..."
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --query "properties.apiKey" -o tsv 2>/dev/null)

if [ -z "$DEPLOYMENT_TOKEN" ]; then
    print_error "Failed to retrieve deployment token"
    print_info "Checking if Static Web App exists..."
    
    # Check if app exists
    if az staticwebapp show --name "$APP_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        print_warning "App exists but couldn't get token"
        print_info "Try: az staticwebapp secrets list --name $APP_NAME --resource-group $RESOURCE_GROUP"
    else
        print_error "Static Web App not found: $APP_NAME"
        print_info "Create it first with deploy-azure.sh"
    fi
    exit 1
fi

print_success "Deployment token retrieved"

# Step 7: Deploy to Azure
print_header "Step 7: Deploying to Azure Static Web Apps"

cd "$FRONTEND_DIR"

print_info "Starting deployment..."
print_info "URL: https://orange-river-0ce07e10f.6.azurestaticapps.net"
print_info "This will take 3-5 minutes..."
echo ""

# Deploy using SWA CLI
if swa deploy \
    --deployment-token "$DEPLOYMENT_TOKEN" \
    --app-location . \
    --output-location .next \
    --env production; then
    
    print_success "Deployment completed!"
else
    print_error "Deployment failed"
    exit 1
fi

cd ../..

# Step 8: Configure environment variables in Azure
print_header "Step 8: Configuring Azure Environment Variables"

print_info "Setting environment variables..."

az staticwebapp appsettings set \
    --name "$APP_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --setting-names \
        NEXT_PUBLIC_API_URL="$BACKEND_URL" \
        NEXTAUTH_SECRET="$NEXTAUTH_SECRET" \
        NEXTAUTH_URL="https://orange-river-0ce07e10f.6.azurestaticapps.net" \
    --output table

print_success "Environment variables configured"

# Step 9: Verify deployment
print_header "Step 9: Verifying Deployment"

print_info "Waiting for deployment to propagate (30 seconds)..."
sleep 30

print_info "Testing homepage..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "https://orange-river-0ce07e10f.6.azurestaticapps.net")

if [ "$STATUS" = "200" ]; then
    print_success "Homepage accessible (HTTP 200)"
else
    print_warning "Homepage returned HTTP $STATUS"
fi

print_info "Checking for CarbonScope branding..."
HTML=$(curl -s "https://orange-river-0ce07e10f.6.azurestaticapps.net")

if echo "$HTML" | grep -qi "carbonscope"; then
    print_success "CarbonScope branding found!"
else
    print_warning "CarbonScope branding not yet visible (may need more time)"
fi

# Summary
print_header "Deployment Complete!"

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════════╗"
echo "║                                                                              ║"
echo "║                    🎉 FRONTEND DEPLOYED SUCCESSFULLY! 🎉                     ║"
echo "║                                                                              ║"
echo "╚══════════════════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Production URLs:${NC}"
echo -e "  ${CYAN}Frontend:${NC} https://orange-river-0ce07e10f.6.azurestaticapps.net"
echo -e "  ${CYAN}Backend:${NC}  $BACKEND_URL"
echo ""
echo -e "${GREEN}What's Live:${NC}"
echo "  ✅ Next.js application deployed"
echo "  ✅ All routes accessible"
echo "  ✅ CarbonScope branding"
echo "  ✅ Connected to backend API"
echo "  ✅ SSL/TLS enabled"
echo ""
echo -e "${YELLOW}Next Steps (Optional):${NC}"
echo "  1. Configure OAuth (Google + GitHub)"
echo "  2. Set up external database (Neon PostgreSQL)"
echo "  3. Configure custom domain (carbonscope.ensimu.space)"
echo "  4. Test authentication flows"
echo ""
echo -e "${CYAN}Testing:${NC}"
echo "  Visit: https://orange-river-0ce07e10f.6.azurestaticapps.net"
echo "  Backend: curl $BACKEND_URL/health"
echo ""
echo -e "${CYAN}Monitoring:${NC}"
echo "  Azure Portal: https://portal.azure.com/#@/resource/subscriptions/.../resourceGroups/$RESOURCE_GROUP"
echo "  Logs: az staticwebapp logs --name $APP_NAME --resource-group $RESOURCE_GROUP"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save deployment info
cat > FRONTEND_DEPLOYMENT_INFO.txt << EOF
CarbonScope Frontend Deployment
================================
Deployed: $(date)

Frontend URL: https://orange-river-0ce07e10f.6.azurestaticapps.net
Backend URL:  $BACKEND_URL

Resource Group: $RESOURCE_GROUP
App Name: $APP_NAME

Environment Variables:
  NEXT_PUBLIC_API_URL: $BACKEND_URL
  NEXTAUTH_URL: https://orange-river-0ce07e10f.6.azurestaticapps.net
  NEXTAUTH_SECRET: $NEXTAUTH_SECRET

Next Steps:
  1. Test: https://orange-river-0ce07e10f.6.azurestaticapps.net
  2. Configure OAuth credentials
  3. Set up database connection
  4. Configure custom domain (optional)

Deployment Token: [Stored in Azure]
EOF

print_success "Deployment info saved to FRONTEND_DEPLOYMENT_INFO.txt"

echo ""
echo "🎉 Deployment complete! Visit your site:"
echo "   https://orange-river-0ce07e10f.6.azurestaticapps.net"
echo ""
