#!/bin/bash

################################################################################
# CarbonScope OAuth Setup Script
# Automated Google & GitHub OAuth configuration using gcloud & gh CLI
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
echo "║     CarbonScope OAuth Automated Setup                         ║"
echo "║     Using gcloud CLI + gh CLI                                 ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
APP_NAME="CarbonScope"
LOCAL_REDIRECT_URI="http://localhost:3000/api/auth/callback"
PROD_DOMAIN="carbonscope-frontend.azurewebsites.net"
PROD_REDIRECT_URI="https://${PROD_DOMAIN}/api/auth/callback"

# Check prerequisites
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    local missing_tools=()
    
    # Check gcloud
    if ! command -v gcloud &> /dev/null; then
        print_warning "gcloud CLI not found"
        missing_tools+=("gcloud")
    else
        print_success "gcloud CLI installed"
    fi
    
    # Check gh
    if ! command -v gh &> /dev/null; then
        print_warning "gh CLI not found"
        missing_tools+=("gh")
    else
        print_success "gh CLI installed"
    fi
    
    if [ ${#missing_tools[@]} -gt 0 ]; then
        echo ""
        print_error "Missing required tools: ${missing_tools[*]}"
        echo ""
        echo "Install them:"
        echo ""
        
        for tool in "${missing_tools[@]}"; do
            if [ "$tool" = "gcloud" ]; then
                echo "  gcloud CLI:"
                echo "    curl https://sdk.cloud.google.com | bash"
                echo "    exec -l \$SHELL"
                echo "    gcloud init"
                echo ""
            elif [ "$tool" = "gh" ]; then
                echo "  gh CLI:"
                echo "    # Ubuntu/Debian:"
                echo "    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg"
                echo "    echo \"deb [arch=\$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main\" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null"
                echo "    sudo apt update"
                echo "    sudo apt install gh"
                echo ""
                echo "    # Or via snap:"
                echo "    sudo snap install gh"
                echo ""
            fi
        done
        
        exit 1
    fi
}

# Setup Google OAuth
setup_google_oauth() {
    print_header "Setting Up Google OAuth"
    
    # Check if logged in
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
        print_info "Not logged in to Google Cloud. Running: gcloud auth login"
        gcloud auth login
    fi
    
    ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -1)
    print_success "Logged in as: $ACCOUNT"
    
    # Get or create project
    echo ""
    print_info "Select or create a Google Cloud project:"
    echo ""
    
    gcloud projects list --format="table(projectId,name,projectNumber)"
    
    echo ""
    read -p "$(echo -e ${BLUE}Enter project ID [or press Enter to create new]: ${NC})" PROJECT_ID
    
    if [ -z "$PROJECT_ID" ]; then
        # Create new project
        PROJECT_ID="carbonscope-$(date +%s)"
        print_info "Creating new project: $PROJECT_ID"
        
        gcloud projects create "$PROJECT_ID" \
            --name="CarbonScope" \
            --set-as-default
        
        print_success "Project created: $PROJECT_ID"
    else
        # Use existing project
        gcloud config set project "$PROJECT_ID"
        print_success "Using project: $PROJECT_ID"
    fi
    
    # Enable required APIs
    print_info "Enabling required APIs..."
    gcloud services enable iamcredentials.googleapis.com --project="$PROJECT_ID" 2>/dev/null || true
    
    # Create OAuth consent screen
    print_info "Configuring OAuth consent screen..."
    
    # Check if consent screen exists
    if ! gcloud alpha iap oauth-brands list --format="value(name)" 2>/dev/null | grep -q .; then
        print_info "Creating OAuth consent screen..."
        
        cat > /tmp/consent-screen.json << EOF
{
  "applicationTitle": "CarbonScope",
  "supportEmail": "${ACCOUNT}",
  "applicationHomePageUrl": "https://${PROD_DOMAIN}",
  "applicationPrivacyPolicyUrl": "https://${PROD_DOMAIN}/legal/privacy",
  "applicationTermsOfServiceUrl": "https://${PROD_DOMAIN}/legal/terms"
}
EOF
        
        # Note: This requires manual setup in newer gcloud versions
        print_warning "OAuth consent screen may need manual configuration"
        print_info "Visit: https://console.cloud.google.com/apis/credentials/consent?project=$PROJECT_ID"
    fi
    
    # Create OAuth client
    print_info "Creating OAuth 2.0 client..."
    
    CLIENT_NAME="${APP_NAME}-web-$(date +%s)"
    
    # Create client
    OAUTH_OUTPUT=$(gcloud alpha iap oauth-clients create "projects/$PROJECT_ID/brands/$(gcloud alpha iap oauth-brands list --format='value(name)' --limit=1 2>/dev/null || echo '')" \
        --display_name="$CLIENT_NAME" 2>&1 || echo "")
    
    # Alternative: Use gcloud API directly
    if [ -z "$OAUTH_OUTPUT" ] || [[ "$OAUTH_OUTPUT" == *"ERROR"* ]]; then
        print_warning "Using alternative method to create OAuth client..."
        
        # Generate client ID and secret
        print_info "Creating OAuth client via REST API..."
        
        ACCESS_TOKEN=$(gcloud auth print-access-token)
        
        RESPONSE=$(curl -s -X POST \
            "https://oauth2.googleapis.com/v2/clients" \
            -H "Authorization: Bearer $ACCESS_TOKEN" \
            -H "Content-Type: application/json" \
            -d '{
                "client_id": "",
                "client_secret": "",
                "redirect_uris": [
                    "'"${LOCAL_REDIRECT_URI}/google"'",
                    "'"${PROD_REDIRECT_URI}/google"'"
                ],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }' 2>&1 || echo "")
        
        if [[ "$RESPONSE" == *"client_id"* ]]; then
            GOOGLE_CLIENT_ID=$(echo "$RESPONSE" | grep -o '"client_id":"[^"]*"' | cut -d'"' -f4)
            GOOGLE_CLIENT_SECRET=$(echo "$RESPONSE" | grep -o '"client_secret":"[^"]*"' | cut -d'"' -f4)
        fi
    fi
    
    # If all automated methods fail, provide manual instructions
    if [ -z "$GOOGLE_CLIENT_ID" ]; then
        print_warning "Automatic OAuth creation requires manual consent screen setup"
        echo ""
        print_info "Please create OAuth client manually:"
        echo ""
        echo "1. Visit: https://console.cloud.google.com/apis/credentials?project=$PROJECT_ID"
        echo "2. Click 'Create Credentials' → 'OAuth client ID'"
        echo "3. Application type: 'Web application'"
        echo "4. Name: 'CarbonScope Web'"
        echo "5. Authorized redirect URIs:"
        echo "   - ${LOCAL_REDIRECT_URI}/google"
        echo "   - ${PROD_REDIRECT_URI}/google"
        echo "6. Click 'Create'"
        echo ""
        read -p "$(echo -e ${BLUE}Enter Google Client ID: ${NC})" GOOGLE_CLIENT_ID
        read -p "$(echo -e ${BLUE}Enter Google Client Secret: ${NC})" GOOGLE_CLIENT_SECRET
    fi
    
    if [ -n "$GOOGLE_CLIENT_ID" ] && [ -n "$GOOGLE_CLIENT_SECRET" ]; then
        print_success "Google OAuth configured!"
        echo "  Client ID: ${GOOGLE_CLIENT_ID:0:20}..."
        echo "  Client Secret: ${GOOGLE_CLIENT_SECRET:0:10}..."
    else
        print_error "Failed to create Google OAuth client"
        GOOGLE_CLIENT_ID=""
        GOOGLE_CLIENT_SECRET=""
    fi
}

# Setup GitHub OAuth
setup_github_oauth() {
    print_header "Setting Up GitHub OAuth"
    
    # Check if logged in
    if ! gh auth status &> /dev/null; then
        print_info "Not logged in to GitHub. Running: gh auth login"
        gh auth login
    fi
    
    USERNAME=$(gh api user -q .login)
    print_success "Logged in as: $USERNAME"
    
    # Create OAuth app
    print_info "Creating GitHub OAuth App..."
    
    APP_NAME_SLUG="${APP_NAME}-$(date +%s)"
    
    # Try to create OAuth app via API
    RESPONSE=$(gh api \
        --method POST \
        -H "Accept: application/vnd.github+json" \
        /user/applications \
        -f name="$APP_NAME_SLUG" \
        -f url="https://${PROD_DOMAIN}" \
        -f callback_url="${LOCAL_REDIRECT_URI}/github" \
        2>&1 || echo "")
    
    if [[ "$RESPONSE" == *"client_id"* ]]; then
        GITHUB_CLIENT_ID=$(echo "$RESPONSE" | jq -r .client_id 2>/dev/null || echo "")
        GITHUB_CLIENT_SECRET=$(echo "$RESPONSE" | jq -r .client_secret 2>/dev/null || echo "")
        
        print_success "GitHub OAuth App created!"
        echo "  Client ID: $GITHUB_CLIENT_ID"
        echo "  Client Secret: ${GITHUB_CLIENT_SECRET:0:10}..."
        
        # Update callback URL to include production
        print_info "Adding production callback URL..."
        gh api \
            --method PATCH \
            -H "Accept: application/vnd.github+json" \
            "/applications/$GITHUB_CLIENT_ID" \
            -f callback_url="${PROD_REDIRECT_URI}/github" \
            2>/dev/null || print_warning "Could not add production URL (add it later)"
    else
        # Manual creation
        print_warning "Automatic OAuth app creation requires additional permissions"
        echo ""
        print_info "Please create OAuth app manually:"
        echo ""
        echo "1. Visit: https://github.com/settings/developers"
        echo "2. Click 'New OAuth App'"
        echo "3. Application name: 'CarbonScope'"
        echo "4. Homepage URL: https://${PROD_DOMAIN}"
        echo "5. Authorization callback URL: ${LOCAL_REDIRECT_URI}/github"
        echo "6. Click 'Register application'"
        echo "7. Click 'Generate a new client secret'"
        echo ""
        
        read -p "$(echo -e ${BLUE}Open GitHub OAuth settings? [y/N]: ${NC})" -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            open "https://github.com/settings/developers" 2>/dev/null || \
            xdg-open "https://github.com/settings/developers" 2>/dev/null || \
            print_info "Visit: https://github.com/settings/developers"
        fi
        
        echo ""
        read -p "$(echo -e ${BLUE}Enter GitHub Client ID: ${NC})" GITHUB_CLIENT_ID
        read -p "$(echo -e ${BLUE}Enter GitHub Client Secret: ${NC})" GITHUB_CLIENT_SECRET
    fi
    
    if [ -n "$GITHUB_CLIENT_ID" ] && [ -n "$GITHUB_CLIENT_SECRET" ]; then
        print_success "GitHub OAuth configured!"
    else
        print_error "Failed to create GitHub OAuth app"
        GITHUB_CLIENT_ID=""
        GITHUB_CLIENT_SECRET=""
    fi
}

# Update environment file
update_env_file() {
    print_header "Updating Environment Variables"
    
    cd apps/frontend
    
    # Generate NEXTAUTH_SECRET if not exists
    if [ ! -f .env.local ]; then
        cp .env.local.template .env.local 2>/dev/null || true
    fi
    
    NEXTAUTH_SECRET=$(openssl rand -base64 32)
    
    # Update .env.local
    cat > .env.local << EOF
# Database (update after Azure deployment)
DATABASE_URL="postgresql://user:password@host:5432/carbonscope_db?sslmode=require"

# NextAuth.js
NEXTAUTH_URL="http://localhost:3000"
NEXTAUTH_SECRET="${NEXTAUTH_SECRET}"

# Google OAuth
GOOGLE_CLIENT_ID="${GOOGLE_CLIENT_ID}"
GOOGLE_CLIENT_SECRET="${GOOGLE_CLIENT_SECRET}"

# GitHub OAuth
GITHUB_CLIENT_ID="${GITHUB_CLIENT_ID}"
GITHUB_CLIENT_SECRET="${GITHUB_CLIENT_SECRET}"

# Backend API
NEXT_PUBLIC_API_URL="http://localhost:8000"
EOF
    
    print_success ".env.local created with OAuth credentials"
    
    cd ../..
}

# Summary
print_summary() {
    print_header "OAuth Setup Complete!"
    
    echo ""
    echo -e "${GREEN}✓ OAuth credentials configured${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "CREDENTIALS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    if [ -n "$GOOGLE_CLIENT_ID" ]; then
        echo -e "${BLUE}Google OAuth:${NC}"
        echo "  Client ID: $GOOGLE_CLIENT_ID"
        echo "  Client Secret: ${GOOGLE_CLIENT_SECRET:0:10}..."
        echo ""
    fi
    
    if [ -n "$GITHUB_CLIENT_ID" ]; then
        echo -e "${BLUE}GitHub OAuth:${NC}"
        echo "  Client ID: $GITHUB_CLIENT_ID"
        echo "  Client Secret: ${GITHUB_CLIENT_SECRET:0:10}..."
        echo ""
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "CONFIGURATION FILE"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "  apps/frontend/.env.local"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "NEXT STEPS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "1. Test authentication locally:"
    echo "   cd apps/frontend"
    echo "   pnpm dev"
    echo "   Visit: http://localhost:3000/auth"
    echo ""
    echo "2. Deploy to Azure:"
    echo "   az login"
    echo "   ./deploy-azure.sh"
    echo ""
    echo "3. After deployment, update OAuth redirect URLs:"
    echo ""
    
    if [ -n "$GOOGLE_CLIENT_ID" ]; then
        echo "   Google: https://console.cloud.google.com/apis/credentials?project=$PROJECT_ID"
        echo "   Add: ${PROD_REDIRECT_URI}/google"
        echo ""
    fi
    
    if [ -n "$GITHUB_CLIENT_ID" ]; then
        echo "   GitHub: https://github.com/settings/developers"
        echo "   Add: ${PROD_REDIRECT_URI}/github"
        echo ""
    fi
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
}

# Main execution
main() {
    check_prerequisites
    
    echo ""
    print_info "This script will set up OAuth credentials for:"
    echo "  • Google Sign-In"
    echo "  • GitHub Sign-In"
    echo ""
    
    read -p "$(echo -e ${YELLOW}Continue? [y/N]: ${NC})" -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "Setup cancelled"
        exit 0
    fi
    
    # Setup OAuth providers
    setup_google_oauth
    setup_github_oauth
    
    # Update env file
    if [ -n "$GOOGLE_CLIENT_ID" ] || [ -n "$GITHUB_CLIENT_ID" ]; then
        update_env_file
        print_summary
    else
        print_error "No OAuth credentials configured"
        exit 1
    fi
    
    print_success "OAuth setup complete! Ready to deploy to Azure."
}

main "$@"
