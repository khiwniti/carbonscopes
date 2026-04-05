#!/bin/bash

################################################################################
# Frontend ACR Deployment Script
# Builds and deploys Next.js frontend to Azure Container Registry + Container Apps
################################################################################

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

################################################################################
# Configuration
################################################################################

PROJECT_NAME="carbonscope"
RESOURCE_GROUP="${PROJECT_NAME}-rg"
LOCATION="eastus"

# Azure Container Registry
ACR_NAME="${PROJECT_NAME}acr"
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"

# Container Apps
CONTAINERAPPS_ENV="${PROJECT_NAME}-env"
FRONTEND_APP="${PROJECT_NAME}-frontend"

# Docker image
IMAGE_NAME="frontend"
IMAGE_TAG="${IMAGE_TAG:-latest}"
FULL_IMAGE_NAME="${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${IMAGE_TAG}"

# Dockerfile
DOCKERFILE="apps/frontend/Dockerfile.production"
BUILD_CONTEXT="."

################################################################################
# Functions
################################################################################

print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_info() { echo -e "${BLUE}→ $1${NC}"; }

check_prerequisites() {
    print_header "Checking Prerequisites"

    # Azure CLI
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI not installed"
        echo "Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
        exit 1
    fi
    print_success "Azure CLI installed"

    # Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker not installed"
        echo "Install from: https://docs.docker.com/get-docker/"
        exit 1
    fi
    print_success "Docker installed"

    # Check Azure login
    if ! az account show &> /dev/null; then
        print_error "Not logged in to Azure"
        print_info "Running: az login"
        az login
    fi

    SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
    print_success "Logged in to Azure: $SUBSCRIPTION_NAME"

    # Check Dockerfile exists
    if [ ! -f "$DOCKERFILE" ]; then
        print_error "Dockerfile not found: $DOCKERFILE"
        exit 1
    fi
    print_success "Dockerfile found: $DOCKERFILE"
}

create_resource_group() {
    print_header "Creating Resource Group"

    if az group exists --name "$RESOURCE_GROUP" | grep -q "true"; then
        print_warning "Resource group '$RESOURCE_GROUP' already exists"
    else
        az group create \
            --name "$RESOURCE_GROUP" \
            --location "$LOCATION" \
            --tags "Project=CarbonScope" "Component=Frontend" "ManagedBy=CLI"
        print_success "Resource group created: $RESOURCE_GROUP"
    fi
}

create_acr() {
    print_header "Creating Azure Container Registry"

    # Check if ACR exists
    if az acr show --name "$ACR_NAME" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        print_warning "ACR '$ACR_NAME' already exists"
    else
        print_info "Creating ACR (this may take 2-3 minutes)..."
        az acr create \
            --name "$ACR_NAME" \
            --resource-group "$RESOURCE_GROUP" \
            --location "$LOCATION" \
            --sku "Basic" \
            --admin-enabled true \
            --tags "Project=CarbonScope" "Component=Registry"

        print_success "ACR created: $ACR_LOGIN_SERVER"
    fi

    # Enable admin user (for easier access)
    az acr update --name "$ACR_NAME" --admin-enabled true &> /dev/null
    print_success "ACR admin user enabled"
}

build_docker_image() {
    print_header "Building Docker Image"

    print_info "Image: $FULL_IMAGE_NAME"
    print_info "Context: $BUILD_CONTEXT"
    print_info "Dockerfile: $DOCKERFILE"
    echo ""

    print_info "Building (this may take 5-10 minutes)..."

    # Build with progress
    docker build \
        -f "$DOCKERFILE" \
        -t "$FULL_IMAGE_NAME" \
        --progress=plain \
        "$BUILD_CONTEXT" 2>&1 | tee /tmp/docker-build.log

    if [ $? -eq 0 ]; then
        print_success "Docker image built successfully"

        # Show image size
        IMAGE_SIZE=$(docker images "$FULL_IMAGE_NAME" --format "{{.Size}}")
        print_info "Image size: $IMAGE_SIZE"
    else
        print_error "Docker build failed. Check /tmp/docker-build.log"
        exit 1
    fi
}

push_to_acr() {
    print_header "Pushing to Azure Container Registry"

    print_info "Logging in to ACR..."
    az acr login --name "$ACR_NAME"
    print_success "ACR login successful"

    print_info "Pushing image (this may take 3-5 minutes)..."
    docker push "$FULL_IMAGE_NAME"

    if [ $? -eq 0 ]; then
        print_success "Image pushed to ACR: $FULL_IMAGE_NAME"
    else
        print_error "Failed to push image to ACR"
        exit 1
    fi

    # Verify image in registry
    print_info "Verifying image in registry..."
    if az acr repository show --name "$ACR_NAME" --image "${IMAGE_NAME}:${IMAGE_TAG}" &> /dev/null; then
        print_success "Image verified in ACR"
    else
        print_warning "Image verification failed (may still be processing)"
    fi
}

create_container_app_environment() {
    print_header "Creating Container Apps Environment"

    # Install containerapp extension if needed
    if ! az extension show --name containerapp &> /dev/null; then
        print_info "Installing Azure Container Apps extension..."
        az extension add --name containerapp --upgrade
        print_success "Extension installed"
    fi

    # Check if environment exists
    if az containerapp env show --name "$CONTAINERAPPS_ENV" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        print_warning "Container Apps environment already exists"
    else
        print_info "Creating Container Apps environment (this may take 3-5 minutes)..."
        az containerapp env create \
            --name "$CONTAINERAPPS_ENV" \
            --resource-group "$RESOURCE_GROUP" \
            --location "$LOCATION" \
            --tags "Project=CarbonScope"

        print_success "Container Apps environment created"
    fi
}

deploy_container_app() {
    print_header "Deploying Container App"

    # Get ACR credentials
    ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query username -o tsv)
    ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query passwords[0].value -o tsv)

    print_info "Deploying frontend container app..."

    # Check if app exists
    if az containerapp show --name "$FRONTEND_APP" --resource-group "$RESOURCE_GROUP" &> /dev/null; then
        print_warning "Container app exists, updating..."

        az containerapp update \
            --name "$FRONTEND_APP" \
            --resource-group "$RESOURCE_GROUP" \
            --image "$FULL_IMAGE_NAME" \
            --registry-server "$ACR_LOGIN_SERVER" \
            --registry-username "$ACR_USERNAME" \
            --registry-password "$ACR_PASSWORD"

        print_success "Container app updated"
    else
        print_info "Creating new container app..."

        az containerapp create \
            --name "$FRONTEND_APP" \
            --resource-group "$RESOURCE_GROUP" \
            --environment "$CONTAINERAPPS_ENV" \
            --image "$FULL_IMAGE_NAME" \
            --target-port 3000 \
            --ingress external \
            --registry-server "$ACR_LOGIN_SERVER" \
            --registry-username "$ACR_USERNAME" \
            --registry-password "$ACR_PASSWORD" \
            --cpu 1.0 \
            --memory 2.0Gi \
            --min-replicas 1 \
            --max-replicas 3 \
            --env-vars \
                "NODE_ENV=production" \
                "NEXT_TELEMETRY_DISABLED=1" \
                "NEXT_PUBLIC_BACKEND_URL=https://carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io" \
            --tags "Project=CarbonScope" "Component=Frontend"

        print_success "Container app created"
    fi

    # Get app URL
    FRONTEND_URL=$(az containerapp show \
        --name "$FRONTEND_APP" \
        --resource-group "$RESOURCE_GROUP" \
        --query properties.configuration.ingress.fqdn -o tsv)

    echo ""
    print_success "Frontend deployed successfully!"
    echo ""
    echo -e "${CYAN}Frontend URL: ${GREEN}https://$FRONTEND_URL${NC}"
    echo ""
}

cleanup_local_images() {
    print_header "Cleanup (Optional)"

    read -p "$(echo -e ${YELLOW}Remove local Docker image? [y/N]: ${NC})" -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rmi "$FULL_IMAGE_NAME" || true
        print_success "Local image removed"
    else
        print_info "Local image retained"
    fi
}

print_deployment_summary() {
    print_header "Deployment Summary"

    FRONTEND_URL=$(az containerapp show \
        --name "$FRONTEND_APP" \
        --resource-group "$RESOURCE_GROUP" \
        --query properties.configuration.ingress.fqdn -o tsv 2>/dev/null || echo "N/A")

    echo ""
    echo -e "${GREEN}✓ Deployment Complete!${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}DEPLOYMENT INFORMATION${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${BLUE}Frontend URL:${NC}"
    echo -e "  ${GREEN}https://$FRONTEND_URL${NC}"
    echo ""
    echo -e "${BLUE}Container Registry:${NC}"
    echo "  $ACR_LOGIN_SERVER"
    echo ""
    echo -e "${BLUE}Image:${NC}"
    echo "  $FULL_IMAGE_NAME"
    echo ""
    echo -e "${BLUE}Resource Group:${NC}"
    echo "  $RESOURCE_GROUP"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${CYAN}USEFUL COMMANDS${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "View logs:"
    echo "  az containerapp logs show --name $FRONTEND_APP --resource-group $RESOURCE_GROUP --follow"
    echo ""
    echo "Scale app:"
    echo "  az containerapp update --name $FRONTEND_APP --resource-group $RESOURCE_GROUP --min-replicas 2 --max-replicas 5"
    echo ""
    echo "View ACR images:"
    echo "  az acr repository list --name $ACR_NAME --output table"
    echo ""
    echo "Redeploy with new tag:"
    echo "  IMAGE_TAG=v2 ./deploy-frontend-acr.sh"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

################################################################################
# Main Execution
################################################################################

main() {
    clear
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                                                               ║"
    echo "║        Frontend ACR Deployment - suna-init                    ║"
    echo "║                                                               ║"
    echo "║        Build → Push → Deploy to Azure Container Apps         ║"
    echo "║                                                               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""

    print_info "Starting deployment process..."
    print_info "Project: $PROJECT_NAME"
    print_info "Location: $LOCATION"
    print_info "Image Tag: $IMAGE_TAG"
    echo ""

    # Confirmation
    read -p "$(echo -e ${YELLOW}Continue with deployment? [y/N]: ${NC})" -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Deployment cancelled"
        exit 0
    fi

    # Pre-flight checks
    check_prerequisites

    # Infrastructure setup
    create_resource_group
    create_acr

    # Docker build and push
    build_docker_image
    push_to_acr

    # Container Apps deployment
    create_container_app_environment
    deploy_container_app

    # Cleanup
    cleanup_local_images

    # Summary
    print_deployment_summary

    print_success "All done! 🚀"
}

# Handle script arguments
case "${1:-}" in
    --build-only)
        print_info "Build only mode"
        check_prerequisites
        build_docker_image
        ;;
    --push-only)
        print_info "Push only mode (image must exist locally)"
        check_prerequisites
        create_acr
        push_to_acr
        ;;
    --deploy-only)
        print_info "Deploy only mode (image must exist in ACR)"
        check_prerequisites
        create_container_app_environment
        deploy_container_app
        print_deployment_summary
        ;;
    *)
        main "$@"
        ;;
esac
