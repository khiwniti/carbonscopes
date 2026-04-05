#!/bin/bash
set -e

echo "========================================"
echo "CarbonScope Frontend Deployment Script"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_info() { echo -e "${YELLOW}→${NC} $1"; }

# Configuration
RESOURCE_GROUP="carbonscope-rg"
STATIC_APP_NAME="carbonscope-frontend"
FRONTEND_DIR="apps/frontend"

# Step 1: Check prerequisites
print_info "Checking prerequisites..."

if ! command -v az &> /dev/null; then
    print_error "Azure CLI not found. Install from: https://docs.microsoft.com/cli/azure/install-azure-cli"
    exit 1
fi
print_success "Azure CLI found"

if ! command -v pnpm &> /dev/null; then
    print_error "pnpm not found. Install with: npm install -g pnpm"
    exit 1
fi
print_success "pnpm found"

# Step 2: Azure login check
print_info "Checking Azure login..."
if ! az account show &> /dev/null; then
    print_error "Not logged in to Azure. Running 'az login'..."
    az login
fi
print_success "Azure login verified"

# Step 3: Get deployment token
print_info "Retrieving deployment token..."
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
  --name "$STATIC_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "properties.apiKey" -o tsv)

if [ -z "$DEPLOYMENT_TOKEN" ]; then
    print_error "Failed to retrieve deployment token"
    exit 1
fi
print_success "Deployment token retrieved"

# Step 4: Navigate to frontend
print_info "Navigating to frontend directory..."
cd "$FRONTEND_DIR"
print_success "In frontend directory: $(pwd)"

# Step 5: Install dependencies
print_info "Installing dependencies..."
pnpm install
print_success "Dependencies installed"

# Step 6: Build application
print_info "Building Next.js application..."
pnpm build
print_success "Build completed"

# Step 7: Install SWA CLI if needed
if ! command -v swa &> /dev/null; then
    print_info "Installing Azure Static Web Apps CLI..."
    npm install -g @azure/static-web-apps-cli
    print_success "SWA CLI installed"
else
    print_success "SWA CLI already installed"
fi

# Step 8: Deploy to Azure Static Web Apps
print_info "Deploying to Azure Static Web Apps..."
swa deploy \
  --deployment-token "$DEPLOYMENT_TOKEN" \
  --app-location . \
  --output-location .next

print_success "Deployment completed!"

# Step 9: Get frontend URL
FRONTEND_URL=$(az staticwebapp show \
  --name "$STATIC_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "defaultHostname" -o tsv)

echo ""
echo "========================================"
echo "Deployment Successful!"
echo "========================================"
echo ""
echo "Frontend URL: https://$FRONTEND_URL"
echo "Backend URL:  https://carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io"
echo ""
echo "Next steps:"
echo "1. Visit frontend URL to verify deployment"
echo "2. Check browser DevTools for any API errors"
echo "3. Test authentication and key features"
echo ""
