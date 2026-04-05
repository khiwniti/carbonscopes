#!/bin/bash

################################################################################
# CarbonScope VM Deployment Script
# Deploy to custom domain: carbonscope.ensimu.space
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
echo "║     CarbonScope VM Deployment                                 ║"
echo "║     Custom Domain: carbonscope.ensimu.space                   ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Configuration
SSH_KEY="/teamspace/studios/this_studio/VM Key.pem"
DOMAIN="carbonscope.ensimu.space"

# Ask for VM IP
echo -e "${YELLOW}Enter your VM IP address:${NC}"
read -p "VM IP: " VM_IP

if [ -z "$VM_IP" ]; then
    print_error "VM IP is required"
    exit 1
fi

# Ask for VM user (default: ubuntu)
echo ""
echo -e "${YELLOW}Enter VM username (default: ubuntu):${NC}"
read -p "Username [ubuntu]: " VM_USER
VM_USER=${VM_USER:-ubuntu}

echo ""
print_info "Configuration:"
echo "  VM IP: $VM_IP"
echo "  VM User: $VM_USER"
echo "  SSH Key: $SSH_KEY"
echo "  Domain: $DOMAIN"
echo ""

read -p "$(echo -e ${YELLOW}Continue with deployment? [y/N]: ${NC})" -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Deployment cancelled"
    exit 0
fi

# Test SSH connection
print_header "Testing SSH Connection"

if ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$VM_USER@$VM_IP" "echo 'SSH connection successful'" > /dev/null 2>&1; then
    print_success "SSH connection successful"
else
    print_error "Cannot connect to VM"
    echo "Please check:"
    echo "  1. VM IP address is correct"
    echo "  2. SSH key has correct permissions (600)"
    echo "  3. VM is running and accessible"
    echo "  4. Port 22 is open in firewall"
    exit 1
fi

# Create deployment package
print_header "Creating Deployment Package"

mkdir -p /tmp/carbonscope-deploy/{nginx,docker}

# Create docker-compose.yml
cat > /tmp/carbonscope-deploy/docker-compose.yml << 'EOF'
version: '3.8'

services:
  frontend:
    image: node:20-alpine
    container_name: carbonscope-frontend
    working_dir: /app
    volumes:
      - ./apps/frontend:/app
      - /app/node_modules
      - /app/.next
    environment:
      - NODE_ENV=production
      - NEXT_PUBLIC_API_URL=https://carbonscope.ensimu.space/api
      - NEXTAUTH_URL=https://carbonscope.ensimu.space
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
      - DATABASE_URL=${DATABASE_URL}
    command: sh -c "corepack enable pnpm && pnpm install && pnpm build && pnpm start"
    ports:
      - "3000:3000"
    restart: unless-stopped
    networks:
      - carbonscope

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.simple
    container_name: carbonscope-backend
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
    ports:
      - "8000:8000"
    restart: unless-stopped
    networks:
      - carbonscope

  nginx:
    image: nginx:alpine
    container_name: carbonscope-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
    networks:
      - carbonscope

networks:
  carbonscope:
    driver: bridge
EOF

# Create nginx.conf
cat > /tmp/carbonscope-deploy/nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    sendfile on;
    keepalive_timeout 65;
    client_max_body_size 100M;

    gzip on;
    gzip_vary on;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    upstream frontend {
        server frontend:3000;
    }

    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name carbonscope.ensimu.space;

        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }

        location /api/ {
            proxy_pass http://backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

# Create .env template
cat > /tmp/carbonscope-deploy/.env << EOF
# Database (use Neon PostgreSQL)
DATABASE_URL=postgresql://user:pass@host/dbname

# Redis (optional)
REDIS_URL=redis://localhost:6379

# NextAuth
NEXTAUTH_SECRET=$(openssl rand -base64 32)
NEXTAUTH_URL=https://carbonscope.ensimu.space

# Google OAuth (get from https://console.cloud.google.com)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# GitHub OAuth (get from https://github.com/settings/developers)
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
EOF

print_success "Deployment package created"

# Upload to VM
print_header "Uploading Files to VM"

# Create directory on VM
ssh -i "$SSH_KEY" "$VM_USER@$VM_IP" "mkdir -p ~/carbonscope/{nginx,apps/frontend,backend}"

# Upload Docker configs
print_info "Uploading Docker configurations..."
scp -i "$SSH_KEY" /tmp/carbonscope-deploy/docker-compose.yml "$VM_USER@$VM_IP:~/carbonscope/"
scp -i "$SSH_KEY" /tmp/carbonscope-deploy/.env "$VM_USER@$VM_IP:~/carbonscope/"
scp -i "$SSH_KEY" /tmp/carbonscope-deploy/nginx/nginx.conf "$VM_USER@$VM_IP:~/carbonscope/nginx/"

# Upload application files
print_info "Uploading application files..."
rsync -avz --progress --exclude 'node_modules' --exclude '.next' --exclude '.git' \
    -e "ssh -i $SSH_KEY" \
    ./apps/frontend/ "$VM_USER@$VM_IP:~/carbonscope/apps/frontend/" 2>&1 | grep -E "sending|sent" | tail -5

rsync -avz --progress --exclude '.venv' --exclude '__pycache__' --exclude '.git' \
    -e "ssh -i $SSH_KEY" \
    ./backend/ "$VM_USER@$VM_IP:~/carbonscope/backend/" 2>&1 | grep -E "sending|sent" | tail -5

print_success "Files uploaded successfully"

# Install Docker on VM (if needed)
print_header "Setting Up VM"

ssh -i "$SSH_KEY" "$VM_USER@$VM_IP" << 'ENDSSH'
# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "✓ Docker installed"
else
    echo "✓ Docker already installed"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo apt update
    sudo apt install docker-compose -y
    echo "✓ Docker Compose installed"
else
    echo "✓ Docker Compose already installed"
fi

# Configure firewall
if command -v ufw &> /dev/null; then
    echo "Configuring firewall..."
    sudo ufw allow 22/tcp
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw --force enable
    echo "✓ Firewall configured"
fi
ENDSSH

print_success "VM setup complete"

# Deploy application
print_header "Deploying Application"

ssh -i "$SSH_KEY" "$VM_USER@$VM_IP" << 'ENDSSH'
cd ~/carbonscope

echo "Stopping existing containers..."
docker-compose down 2>/dev/null || true

echo "Starting containers..."
docker-compose up -d --build

echo "Waiting for containers to start..."
sleep 10

echo "Container status:"
docker-compose ps
ENDSSH

print_success "Application deployed!"

# Summary
print_header "Deployment Complete!"

echo ""
echo -e "${GREEN}✓ CarbonScope successfully deployed!${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "NEXT STEPS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Configure Cloudflare DNS:"
echo "   • Login to: https://dash.cloudflare.com"
echo "   • Domain: ensimu.space"
echo "   • Add A record: carbonscope → $VM_IP"
echo "   • Enable proxy (orange cloud)"
echo ""
echo "2. Update environment variables:"
echo "   ssh -i \"$SSH_KEY\" $VM_USER@$VM_IP"
echo "   cd ~/carbonscope"
echo "   nano .env"
echo "   # Add your DATABASE_URL, OAuth credentials, etc."
echo "   docker-compose restart"
echo ""
echo "3. Test your deployment:"
echo "   http://$VM_IP (direct IP)"
echo "   http://carbonscope.ensimu.space (after DNS propagation)"
echo ""
echo "4. View logs:"
echo "   ssh -i \"$SSH_KEY\" $VM_USER@$VM_IP"
echo "   cd ~/carbonscope && docker-compose logs -f"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Cleanup
rm -rf /tmp/carbonscope-deploy

print_success "Deployment script completed!"
