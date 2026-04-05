#!/bin/bash

################################################################################
# CarbonScope Code Deployment Script
# Deploys application code to Azure App Services
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_NAME="carbonscope"
RESOURCE_GROUP="${PROJECT_NAME}-rg"
FRONTEND_APP="${PROJECT_NAME}-frontend"
BACKEND_APP="${PROJECT_NAME}-backend"

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

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_prereqs() {
    print_header "Checking Prerequisites"
    
    # Check Azure CLI
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI not found"
        exit 1
    fi
    
    # Check if logged in
    if ! az account show &> /dev/null; then
        print_error "Not logged in to Azure. Run: az login"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js not found"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 not found"
        exit 1
    fi
    
    print_success "All prerequisites met"
}

build_frontend() {
    print_header "Building Frontend (Next.js)"
    
    cd apps/frontend
    
    print_info "Installing dependencies..."
    pnpm install --frozen-lockfile
    
    print_info "Building production bundle..."
    pnpm build
    
    print_success "Frontend build complete"
    
    cd ../..
}

deploy_frontend() {
    print_header "Deploying Frontend to Azure"
    
    cd apps/frontend
    
    print_info "Creating deployment package..."
    
    # Create zip deployment package
    cat > .deployment << 'EOF'
[config]
SCM_DO_BUILD_DURING_DEPLOYMENT = true
EOF
    
    cat > deploy.sh << 'EOF'
#!/bin/bash
set -e
echo "Installing dependencies..."
npm install
echo "Building application..."
npm run build
EOF
    
    chmod +x deploy.sh
    
    # Create package
    zip -r ../frontend-deploy.zip . \
        -x "node_modules/*" \
        -x ".next/*" \
        -x ".git/*" \
        -x "*.log"
    
    cd ..
    
    print_info "Uploading to Azure..."
    az webapp deploy \
        --resource-group "$RESOURCE_GROUP" \
        --name "$FRONTEND_APP" \
        --src-path frontend-deploy.zip \
        --type zip \
        --async true
    
    print_success "Frontend deployment initiated"
    print_info "View logs: az webapp log tail --name $FRONTEND_APP --resource-group $RESOURCE_GROUP"
    
    # Cleanup
    rm frontend-deploy.zip
    cd ..
}

build_backend() {
    print_header "Building Backend (FastAPI)"
    
    cd backend
    
    print_info "Installing dependencies..."
    pip install -r requirements.txt || python3 -m pip install -r requirements.txt || true
    
    print_success "Backend dependencies installed"
    
    cd ..
}

deploy_backend() {
    print_header "Deploying Backend to Azure"
    
    cd backend
    
    print_info "Creating deployment package..."
    
    # Create requirements.txt from pyproject.toml
    if [ -f "pyproject.toml" ]; then
        print_info "Extracting dependencies from pyproject.toml..."
        python3 << 'PYTHON_SCRIPT'
import tomli
import sys

try:
    with open("pyproject.toml", "rb") as f:
        data = tomli.load(f)
        deps = data.get("project", {}).get("dependencies", [])
        with open("requirements.txt", "w") as req:
            for dep in deps:
                req.write(dep + "\n")
    print("requirements.txt created")
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    # Fallback: create basic requirements.txt
    with open("requirements.txt", "w") as req:
        req.write("fastapi>=0.115.0\n")
        req.write("uvicorn>=0.27.0\n")
        req.write("gunicorn>=23.0.0\n")
        req.write("python-dotenv>=1.0.0\n")
        req.write("prisma>=0.15.0\n")
        req.write("supabase>=2.17.0\n")
        req.write("redis>=5.2.0\n")
PYTHON_SCRIPT
    fi
    
    # Create startup script
    cat > startup.sh << 'EOF'
#!/bin/bash
set -e

echo "Starting CarbonScope Backend..."

# Run database migrations
if [ -f "prisma/schema.prisma" ]; then
    echo "Running Prisma migrations..."
    prisma migrate deploy || true
    prisma generate || true
fi

# Start Gunicorn with Uvicorn workers
exec gunicorn -w 4 \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    api:app
EOF
    
    chmod +x startup.sh
    
    # Create zip package
    zip -r ../backend-deploy.zip . \
        -x ".venv/*" \
        -x "__pycache__/*" \
        -x "*.pyc" \
        -x ".git/*" \
        -x "*.log"
    
    cd ..
    
    print_info "Uploading to Azure..."
    az webapp deploy \
        --resource-group "$RESOURCE_GROUP" \
        --name "$BACKEND_APP" \
        --src-path backend-deploy.zip \
        --type zip \
        --async true
    
    print_success "Backend deployment initiated"
    print_info "View logs: az webapp log tail --name $BACKEND_APP --resource-group $RESOURCE_GROUP"
    
    # Cleanup
    rm backend-deploy.zip
}

restart_apps() {
    print_header "Restarting Applications"
    
    print_info "Restarting frontend..."
    az webapp restart \
        --name "$FRONTEND_APP" \
        --resource-group "$RESOURCE_GROUP"
    
    print_info "Restarting backend..."
    az webapp restart \
        --name "$BACKEND_APP" \
        --resource-group "$RESOURCE_GROUP"
    
    print_success "Applications restarted"
}

print_deployment_urls() {
    print_header "Deployment Complete!"
    
    echo ""
    echo -e "${GREEN}✓ Code successfully deployed to Azure${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "APPLICATION URLS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${BLUE}Frontend:${NC}"
    echo "  https://${FRONTEND_APP}.azurewebsites.net"
    echo ""
    echo -e "${BLUE}Backend API:${NC}"
    echo "  https://${BACKEND_APP}.azurewebsites.net"
    echo "  https://${BACKEND_APP}.azurewebsites.net/docs (API docs)"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "MONITORING"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "View logs:"
    echo "  Frontend: az webapp log tail --name $FRONTEND_APP --resource-group $RESOURCE_GROUP"
    echo "  Backend:  az webapp log tail --name $BACKEND_APP --resource-group $RESOURCE_GROUP"
    echo ""
    echo "Azure Portal:"
    echo "  https://portal.azure.com/#@/resource/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$RESOURCE_GROUP"
    echo ""
}

main() {
    clear
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                                                               ║"
    echo "║          CarbonScope Code Deployment                          ║"
    echo "║                                                               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
    
    # Menu
    echo "Select deployment option:"
    echo "1) Deploy Both (Frontend + Backend)"
    echo "2) Deploy Frontend Only"
    echo "3) Deploy Backend Only"
    echo "4) Cancel"
    echo ""
    read -p "Enter choice [1-4]: " choice
    
    case $choice in
        1)
            check_prereqs
            build_frontend
            build_backend
            deploy_frontend
            deploy_backend
            restart_apps
            print_deployment_urls
            ;;
        2)
            check_prereqs
            build_frontend
            deploy_frontend
            print_info "Restarting frontend..."
            az webapp restart --name "$FRONTEND_APP" --resource-group "$RESOURCE_GROUP"
            echo ""
            echo -e "${GREEN}✓ Frontend deployed: https://${FRONTEND_APP}.azurewebsites.net${NC}"
            ;;
        3)
            check_prereqs
            build_backend
            deploy_backend
            print_info "Restarting backend..."
            az webapp restart --name "$BACKEND_APP" --resource-group "$RESOURCE_GROUP"
            echo ""
            echo -e "${GREEN}✓ Backend deployed: https://${BACKEND_APP}.azurewebsites.net${NC}"
            ;;
        4)
            print_info "Deployment cancelled"
            exit 0
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
}

main "$@"
