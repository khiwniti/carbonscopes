#!/bin/bash
set -e

echo "=========================================="
echo "Azure Static Web Apps Deployment"
echo "Deploying source code - Azure will build"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_info() { echo -e "${YELLOW}→${NC} $1"; }

# Configuration
RESOURCE_GROUP="carbonscope-rg"
STATIC_APP_NAME="carbonscope-frontend"
BACKEND_URL="https://carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io"

# Check Azure CLI
if ! command -v az &> /dev/null; then
    print_error "Azure CLI not found"
    exit 1
fi
print_success "Azure CLI found"

# Check login
print_info "Checking Azure login..."
if ! az account show &> /dev/null; then
    print_error "Not logged in. Run: az login"
    exit 1
fi
print_success "Azure login verified"

# Get deployment token
print_info "Getting deployment token..."
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
  --name "$STATIC_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "properties.apiKey" -o tsv 2>/dev/null)

if [ -z "$DEPLOYMENT_TOKEN" ]; then
    print_error "Failed to get deployment token"
    print_info "Creating Static Web App..."

    az staticwebapp create \
      --name "$STATIC_APP_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --location "eastus" \
      --sku Free \
      --output none

    print_success "Static Web App created"

    DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
      --name "$STATIC_APP_NAME" \
      --resource-group "$RESOURCE_GROUP" \
      --query "properties.apiKey" -o tsv)
fi

print_success "Deployment token retrieved"

# Install SWA CLI if needed
if ! command -v swa &> /dev/null; then
    print_info "Installing Azure Static Web Apps CLI..."
    npm install -g @azure/static-web-apps-cli
    print_success "SWA CLI installed"
fi

# Navigate to project root (monorepo)
cd /teamspace/studios/this_studio/comprehensive-carbonscope-bim-agent/carbonscope-init

print_info "Deploying to Azure Static Web Apps..."
print_info "Azure will build the project in the cloud (16GB RAM available)"

# Deploy source code for Azure to build
swa deploy \
  --deployment-token "$DEPLOYMENT_TOKEN" \
  --app-location "apps/frontend" \
  --api-location "" \
  --output-location ".next" \
  --env "production" \
  --verbose

print_success "Deployment initiated!"

echo ""
echo "=========================================="
echo "Deployment Status"
echo "=========================================="
echo ""

# Get frontend URL
FRONTEND_URL=$(az staticwebapp show \
  --name "$STATIC_APP_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "defaultHostname" -o tsv 2>/dev/null || echo "orange-river-0ce07e10f.6.azurestaticapps.net")

echo "Frontend URL: https://$FRONTEND_URL"
echo "Backend URL:  $BACKEND_URL"
echo ""
echo "Build is running in Azure cloud..."
echo "Monitor at: https://portal.azure.com"
echo ""
echo "Expected build time: 5-10 minutes"
echo ""
