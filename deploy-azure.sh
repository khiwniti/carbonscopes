#!/bin/bash

################################################################################
# CarbonScope Azure Deployment Script
# Full-stack deployment to Azure using Azure CLI
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="carbonscope"
RESOURCE_GROUP="${PROJECT_NAME}-rg"
LOCATION="eastus"  # Change to your preferred region
ENVIRONMENT="production"  # production, staging, development

# App Service Plans
FRONTEND_PLAN="${PROJECT_NAME}-frontend-plan"
BACKEND_PLAN="${PROJECT_NAME}-backend-plan"

# App Services
FRONTEND_APP="${PROJECT_NAME}-frontend"
BACKEND_APP="${PROJECT_NAME}-backend"

# Database
POSTGRES_SERVER="${PROJECT_NAME}-postgres"
POSTGRES_DB="carbonscope_db"
POSTGRES_ADMIN="carbonscope_admin"

# Redis
REDIS_NAME="${PROJECT_NAME}-redis"

# Storage
STORAGE_ACCOUNT="${PROJECT_NAME}storage"

# Container Registry (if using containers)
ACR_NAME="${PROJECT_NAME}acr"

# Key Vault (for secrets)
KEYVAULT_NAME="${PROJECT_NAME}-kv"

# Application Insights
APPINSIGHTS_NAME="${PROJECT_NAME}-insights"

# Tags
TAGS="Environment=${ENVIRONMENT} Project=CarbonScope ManagedBy=AzureCLI"

################################################################################
# Functions
################################################################################

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

check_azure_cli() {
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI not found. Please install it first:"
        echo "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    print_success "Azure CLI installed"
}

check_login() {
    if ! az account show &> /dev/null; then
        print_warning "Not logged in to Azure"
        print_info "Running: az login"
        az login
    fi
    
    SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
    print_success "Logged in to Azure (Subscription: $SUBSCRIPTION_NAME)"
}

create_resource_group() {
    print_header "Creating Resource Group"
    
    if az group exists --name "$RESOURCE_GROUP" | grep -q "true"; then
        print_warning "Resource group '$RESOURCE_GROUP' already exists"
    else
        az group create \
            --name "$RESOURCE_GROUP" \
            --location "$LOCATION" \
            --tags $TAGS
        print_success "Resource group '$RESOURCE_GROUP' created"
    fi
}

create_app_insights() {
    print_header "Creating Application Insights"
    
    az monitor app-insights component create \
        --app "$APPINSIGHTS_NAME" \
        --location "$LOCATION" \
        --resource-group "$RESOURCE_GROUP" \
        --tags $TAGS \
        || print_warning "Application Insights may already exist"
    
    APPINSIGHTS_KEY=$(az monitor app-insights component show \
        --app "$APPINSIGHTS_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query instrumentationKey -o tsv)
    
    print_success "Application Insights created (Key: ${APPINSIGHTS_KEY:0:10}...)"
}

create_key_vault() {
    print_header "Creating Key Vault"
    
    az keyvault create \
        --name "$KEYVAULT_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --tags $TAGS \
        --enabled-for-deployment true \
        --enabled-for-template-deployment true \
        || print_warning "Key Vault may already exist"
    
    print_success "Key Vault '$KEYVAULT_NAME' created"
}

create_postgres() {
    print_header "Creating PostgreSQL Database"
    
    print_info "Generating secure password..."
    POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    
    print_info "Creating PostgreSQL Flexible Server (this may take 5-10 minutes)..."
    az postgres flexible-server create \
        --name "$POSTGRES_SERVER" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --admin-user "$POSTGRES_ADMIN" \
        --admin-password "$POSTGRES_PASSWORD" \
        --sku-name "Standard_B1ms" \
        --tier "Burstable" \
        --storage-size 32 \
        --version "15" \
        --public-access "0.0.0.0" \
        --tags $TAGS \
        || print_warning "PostgreSQL server may already exist"
    
    print_info "Creating database..."
    az postgres flexible-server db create \
        --resource-group "$RESOURCE_GROUP" \
        --server-name "$POSTGRES_SERVER" \
        --database-name "$POSTGRES_DB" \
        || print_warning "Database may already exist"
    
    # Store password in Key Vault
    az keyvault secret set \
        --vault-name "$KEYVAULT_NAME" \
        --name "postgres-password" \
        --value "$POSTGRES_PASSWORD"
    
    POSTGRES_HOST="${POSTGRES_SERVER}.postgres.database.azure.com"
    print_success "PostgreSQL created: $POSTGRES_HOST"
    print_info "Password stored in Key Vault"
}

create_redis() {
    print_header "Creating Redis Cache"
    
    az redis create \
        --name "$REDIS_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --sku "Basic" \
        --vm-size "C0" \
        --tags $TAGS \
        || print_warning "Redis may already exist"
    
    print_info "Retrieving Redis connection string..."
    REDIS_KEY=$(az redis list-keys \
        --name "$REDIS_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query primaryKey -o tsv)
    
    # Store in Key Vault
    az keyvault secret set \
        --vault-name "$KEYVAULT_NAME" \
        --name "redis-key" \
        --value "$REDIS_KEY"
    
    print_success "Redis Cache created"
}

create_storage() {
    print_header "Creating Storage Account"
    
    az storage account create \
        --name "$STORAGE_ACCOUNT" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --sku "Standard_LRS" \
        --kind "StorageV2" \
        --tags $TAGS \
        || print_warning "Storage account may already exist"
    
    print_info "Creating blob containers..."
    STORAGE_KEY=$(az storage account keys list \
        --account-name "$STORAGE_ACCOUNT" \
        --resource-group "$RESOURCE_GROUP" \
        --query "[0].value" -o tsv)
    
    az storage container create \
        --name "uploads" \
        --account-name "$STORAGE_ACCOUNT" \
        --account-key "$STORAGE_KEY" \
        --public-access off
    
    az storage container create \
        --name "static" \
        --account-name "$STORAGE_ACCOUNT" \
        --account-key "$STORAGE_KEY" \
        --public-access blob
    
    # Store in Key Vault
    az keyvault secret set \
        --vault-name "$KEYVAULT_NAME" \
        --name "storage-key" \
        --value "$STORAGE_KEY"
    
    print_success "Storage Account created with containers"
}

create_frontend_app() {
    print_header "Creating Frontend App Service (Next.js)"
    
    # Create App Service Plan
    az appservice plan create \
        --name "$FRONTEND_PLAN" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --is-linux \
        --sku "B1" \
        --tags $TAGS \
        || print_warning "Frontend plan may already exist"
    
    # Create Web App
    az webapp create \
        --name "$FRONTEND_APP" \
        --resource-group "$RESOURCE_GROUP" \
        --plan "$FRONTEND_PLAN" \
        --runtime "NODE:20-lts" \
        --tags $TAGS \
        || print_warning "Frontend app may already exist"
    
    # Configure deployment settings
    az webapp config set \
        --name "$FRONTEND_APP" \
        --resource-group "$RESOURCE_GROUP" \
        --startup-file "node_modules/.bin/next start -p 8080" \
        --use-32bit-worker-process false
    
    # Configure app settings
    az webapp config appsettings set \
        --name "$FRONTEND_APP" \
        --resource-group "$RESOURCE_GROUP" \
        --settings \
            "NODE_ENV=production" \
            "WEBSITE_NODE_DEFAULT_VERSION=20" \
            "SCM_DO_BUILD_DURING_DEPLOYMENT=true" \
            "APPLICATIONINSIGHTS_CONNECTION_STRING=@Microsoft.KeyVault(SecretUri=https://${KEYVAULT_NAME}.vault.azure.net/secrets/appinsights-connection-string/)" \
            "NEXT_PUBLIC_SITE_URL=https://${FRONTEND_APP}.azurewebsites.net"
    
    FRONTEND_URL="https://${FRONTEND_APP}.azurewebsites.net"
    print_success "Frontend App Service created: $FRONTEND_URL"
}

create_backend_app() {
    print_header "Creating Backend App Service (FastAPI)"
    
    # Create App Service Plan
    az appservice plan create \
        --name "$BACKEND_PLAN" \
        --resource-group "$RESOURCE_GROUP" \
        --location "$LOCATION" \
        --is-linux \
        --sku "B1" \
        --tags $TAGS \
        || print_warning "Backend plan may already exist"
    
    # Create Web App
    az webapp create \
        --name "$BACKEND_APP" \
        --resource-group "$RESOURCE_GROUP" \
        --plan "$BACKEND_PLAN" \
        --runtime "PYTHON:3.11" \
        --tags $TAGS \
        || print_warning "Backend app may already exist"
    
    # Configure deployment settings
    az webapp config set \
        --name "$BACKEND_APP" \
        --resource-group "$RESOURCE_GROUP" \
        --startup-file "gunicorn -w 4 -k uvicorn.workers.UvicornWorker api:app --bind 0.0.0.0:8000" \
        --use-32bit-worker-process false
    
    # Get database connection info
    POSTGRES_HOST="${POSTGRES_SERVER}.postgres.database.azure.com"
    POSTGRES_PASSWORD=$(az keyvault secret show \
        --vault-name "$KEYVAULT_NAME" \
        --name "postgres-password" \
        --query value -o tsv)
    
    DATABASE_URL="postgresql://${POSTGRES_ADMIN}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${POSTGRES_DB}?sslmode=require"
    
    # Configure app settings
    az webapp config appsettings set \
        --name "$BACKEND_APP" \
        --resource-group "$RESOURCE_GROUP" \
        --settings \
            "PYTHON_VERSION=3.11" \
            "SCM_DO_BUILD_DURING_DEPLOYMENT=true" \
            "DATABASE_URL=@Microsoft.KeyVault(SecretUri=https://${KEYVAULT_NAME}.vault.azure.net/secrets/database-url/)" \
            "REDIS_URL=@Microsoft.KeyVault(SecretUri=https://${KEYVAULT_NAME}.vault.azure.net/secrets/redis-url/)" \
            "ENVIRONMENT=production" \
            "APPLICATIONINSIGHTS_CONNECTION_STRING=@Microsoft.KeyVault(SecretUri=https://${KEYVAULT_NAME}.vault.azure.net/secrets/appinsights-connection-string/)"
    
    # Store DATABASE_URL in Key Vault
    az keyvault secret set \
        --vault-name "$KEYVAULT_NAME" \
        --name "database-url" \
        --value "$DATABASE_URL"
    
    BACKEND_URL="https://${BACKEND_APP}.azurewebsites.net"
    print_success "Backend App Service created: $BACKEND_URL"
}

configure_cors() {
    print_header "Configuring CORS"
    
    FRONTEND_URL="https://${FRONTEND_APP}.azurewebsites.net"
    
    az webapp cors add \
        --name "$BACKEND_APP" \
        --resource-group "$RESOURCE_GROUP" \
        --allowed-origins "$FRONTEND_URL" "https://localhost:3000"
    
    print_success "CORS configured for backend"
}

setup_managed_identity() {
    print_header "Setting up Managed Identity"
    
    # Enable system-assigned managed identity for apps
    az webapp identity assign \
        --name "$FRONTEND_APP" \
        --resource-group "$RESOURCE_GROUP"
    
    az webapp identity assign \
        --name "$BACKEND_APP" \
        --resource-group "$RESOURCE_GROUP"
    
    # Get managed identity principal IDs
    FRONTEND_IDENTITY=$(az webapp identity show \
        --name "$FRONTEND_APP" \
        --resource-group "$RESOURCE_GROUP" \
        --query principalId -o tsv)
    
    BACKEND_IDENTITY=$(az webapp identity show \
        --name "$BACKEND_APP" \
        --resource-group "$RESOURCE_GROUP" \
        --query principalId -o tsv)
    
    # Grant Key Vault access
    az keyvault set-policy \
        --name "$KEYVAULT_NAME" \
        --object-id "$FRONTEND_IDENTITY" \
        --secret-permissions get list
    
    az keyvault set-policy \
        --name "$KEYVAULT_NAME" \
        --object-id "$BACKEND_IDENTITY" \
        --secret-permissions get list
    
    print_success "Managed Identity configured with Key Vault access"
}

print_deployment_info() {
    print_header "Deployment Complete!"
    
    echo ""
    echo -e "${GREEN}✓ CarbonScope successfully deployed to Azure${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "DEPLOYMENT INFORMATION"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${BLUE}Frontend URL:${NC}"
    echo "  https://${FRONTEND_APP}.azurewebsites.net"
    echo ""
    echo -e "${BLUE}Backend API URL:${NC}"
    echo "  https://${BACKEND_APP}.azurewebsites.net"
    echo ""
    echo -e "${BLUE}PostgreSQL Server:${NC}"
    echo "  ${POSTGRES_SERVER}.postgres.database.azure.com"
    echo ""
    echo -e "${BLUE}Redis Cache:${NC}"
    echo "  ${REDIS_NAME}.redis.cache.windows.net"
    echo ""
    echo -e "${BLUE}Storage Account:${NC}"
    echo "  ${STORAGE_ACCOUNT}.blob.core.windows.net"
    echo ""
    echo -e "${BLUE}Key Vault:${NC}"
    echo "  ${KEYVAULT_NAME}.vault.azure.net"
    echo ""
    echo -e "${BLUE}Resource Group:${NC}"
    echo "  $RESOURCE_GROUP"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "NEXT STEPS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. Deploy your code:"
    echo "   Frontend: cd apps/frontend && az webapp up --name $FRONTEND_APP"
    echo "   Backend:  cd backend && az webapp up --name $BACKEND_APP"
    echo ""
    echo "2. Configure environment variables in Azure Portal"
    echo "   or use: az webapp config appsettings set"
    echo ""
    echo "3. Set up custom domain (optional):"
    echo "   az webapp config hostname add"
    echo ""
    echo "4. Enable SSL certificate:"
    echo "   az webapp config ssl bind"
    echo ""
    echo "5. Set up CI/CD with GitHub Actions (see .github/workflows/)"
    echo ""
    echo "6. View secrets in Key Vault:"
    echo "   az keyvault secret list --vault-name $KEYVAULT_NAME"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

print_cost_estimate() {
    print_header "Cost Estimate (Monthly)"
    
    echo ""
    echo "Based on selected SKUs:"
    echo ""
    echo "• App Service Plan (Frontend) - B1:    ~\$13"
    echo "• App Service Plan (Backend) - B1:     ~\$13"
    echo "• PostgreSQL Flexible Server - B1ms:   ~\$12"
    echo "• Redis Cache - Basic C0:              ~\$16"
    echo "• Storage Account - LRS:               ~\$1"
    echo "• Application Insights:                ~\$2"
    echo "• Key Vault:                           ~\$0.30"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Total (estimated):                     ~\$57/month"
    echo ""
    echo -e "${YELLOW}Note: Actual costs may vary based on usage${NC}"
    echo ""
}

################################################################################
# Main Deployment Flow
################################################################################

main() {
    clear
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                                                               ║"
    echo "║          CarbonScope Azure Deployment Script                  ║"
    echo "║                                                               ║"
    echo "║          BKS - Embodied Carbon Intelligence Platform          ║"
    echo "║                                                               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    
    print_info "Starting deployment to Azure..."
    print_info "Region: $LOCATION"
    print_info "Environment: $ENVIRONMENT"
    echo ""
    
    # Confirmation
    read -p "$(echo -e ${YELLOW}Continue with deployment? [y/N]: ${NC})" -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled"
        exit 0
    fi
    
    # Pre-flight checks
    check_azure_cli
    check_login
    
    # Cost estimate
    print_cost_estimate
    read -p "$(echo -e ${YELLOW}Proceed with these estimated costs? [y/N]: ${NC})" -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled"
        exit 0
    fi
    
    # Infrastructure deployment
    create_resource_group
    create_app_insights
    create_key_vault
    create_postgres
    create_redis
    create_storage
    create_frontend_app
    create_backend_app
    configure_cors
    setup_managed_identity
    
    # Summary
    print_deployment_info
    
    print_success "Infrastructure deployment complete!"
    print_info "Run './deploy-code.sh' to deploy your application code"
}

# Run main function
main "$@"
