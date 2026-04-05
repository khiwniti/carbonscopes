# CarbonScope VM Deployment Guide

**Date:** March 28, 2026  
**Custom Domain:** carbonscope.ensimu.space  
**VM Key:** /teamspace/studios/this_studio/VM Key.pem  

---

## 🎯 Overview

Deploy CarbonScope to your VM with:
- Custom domain: `carbonscope.ensimu.space`
- Cloudflare DNS + SSL
- Docker + Docker Compose
- Nginx reverse proxy
- Auto-renewal SSL certificates
- Production-ready setup

---

## 📋 Prerequisites

### 1. VM Requirements

- **OS:** Ubuntu 20.04+ / Debian 11+
- **RAM:** 2GB minimum (4GB recommended)
- **Storage:** 20GB minimum
- **CPU:** 2 cores minimum
- **Ports:** 80, 443, 22 open

### 2. SSH Access

```bash
# Test SSH connection
ssh -i "/teamspace/studios/this_studio/VM Key.pem" ubuntu@YOUR_VM_IP

# Replace YOUR_VM_IP with your actual VM IP address
```

### 3. Domain Setup

- Domain: `carbonscope.ensimu.space`
- DNS Provider: Cloudflare
- Need: Cloudflare account access

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. SSH into VM
ssh -i "/teamspace/studios/this_studio/VM Key.pem" ubuntu@YOUR_VM_IP

# 2. Run automated setup
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 3. Deploy CarbonScope
git clone YOUR_REPO
cd carbonscope && docker-compose up -d
```

---

## 📖 Detailed Deployment Steps

### Step 1: Get VM Information

First, we need your VM IP address. You should have this from your cloud provider (AWS, Azure, GCP, DigitalOcean, etc.).

```bash
# Find your VM IP
# Check your cloud provider dashboard or:
ssh -i "/teamspace/studios/this_studio/VM Key.pem" ubuntu@YOUR_VM_IP "curl -s ifconfig.me"
```

### Step 2: Initial VM Setup

```bash
# SSH into your VM
ssh -i "/teamspace/studios/this_studio/VM Key.pem" ubuntu@YOUR_VM_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Install other utilities
sudo apt install git curl wget ufw -y

# Configure firewall
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable

# Logout and login again for docker group to take effect
exit
```

### Step 3: Cloudflare DNS Configuration

#### A. Login to Cloudflare

1. Go to https://dash.cloudflare.com
2. Select your domain: `ensimu.space`
3. Go to **DNS** → **Records**

#### B. Add DNS Record

**Type:** A Record  
**Name:** `carbonscope`  
**IPv4 address:** `YOUR_VM_IP`  
**Proxy status:** ☁️ Proxied (orange cloud)  
**TTL:** Auto  

Click **Save**

#### C. SSL/TLS Settings

1. Go to **SSL/TLS** → **Overview**
2. Set encryption mode: **Full (strict)**
3. Go to **SSL/TLS** → **Edge Certificates**
4. Enable:
   - ✅ Always Use HTTPS
   - ✅ Automatic HTTPS Rewrites
   - ✅ Minimum TLS Version: 1.2

### Step 4: Deploy CarbonScope

SSH back into your VM:

```bash
ssh -i "/teamspace/studios/this_studio/VM Key.pem" ubuntu@YOUR_VM_IP

# Create project directory
mkdir -p ~/carbonscope
cd ~/carbonscope

# We'll upload files in next step
```

---

## 🐳 Docker Compose Configuration

### docker-compose.yml

```yaml
version: '3.8'

services:
  # Frontend (Next.js)
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
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}
      - GITHUB_CLIENT_ID=${GITHUB_CLIENT_ID}
      - GITHUB_CLIENT_SECRET=${GITHUB_CLIENT_SECRET}
    command: sh -c "corepack enable pnpm && pnpm install && pnpm build && pnpm start"
    ports:
      - "3000:3000"
    restart: unless-stopped
    networks:
      - carbonscope-network

  # Backend (FastAPI)
  backend:
    image: python:3.11-slim
    container_name: carbonscope-backend
    working_dir: /app
    volumes:
      - ./backend:/app
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    command: sh -c "pip install --no-cache-dir fastapi uvicorn && uvicorn simple_api:app --host 0.0.0.0 --port 8000"
    ports:
      - "8000:8000"
    restart: unless-stopped
    networks:
      - carbonscope-network

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: carbonscope-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
    networks:
      - carbonscope-network

networks:
  carbonscope-network:
    driver: bridge
```

### Nginx Configuration

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;

    # SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    # Upstream definitions
    upstream frontend {
        server frontend:3000;
    }

    upstream backend {
        server backend:8000;
    }

    # HTTP redirect to HTTPS
    server {
        listen 80;
        server_name carbonscope.ensimu.space;
        
        # Allow Cloudflare to verify SSL
        location /.well-known/ {
            root /var/www/html;
        }
        
        # Redirect all HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name carbonscope.ensimu.space;

        # Cloudflare Origin Certificate (if using)
        # ssl_certificate /etc/nginx/ssl/cert.pem;
        # ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "no-referrer-when-downgrade" always;

        # Frontend (Next.js)
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

        # Backend API
        location /api/ {
            proxy_pass http://backend/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # WebSocket support
        location /ws {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }
}
```

### Environment Variables

Create `.env`:

```bash
# Database (use Neon PostgreSQL free tier)
DATABASE_URL=postgresql://user:pass@host/dbname

# Redis (use Upstash free tier)
REDIS_URL=redis://default:pass@host:6379

# NextAuth
NEXTAUTH_SECRET=your-generated-secret-from-openssl-rand-base64-32
NEXTAUTH_URL=https://carbonscope.ensimu.space

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# GitHub OAuth
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

---

## 📦 Deployment Script

Create `deploy.sh` on your VM:

```bash
#!/bin/bash

echo "🚀 Deploying CarbonScope to carbonscope.ensimu.space"
echo ""

# Pull latest code
git pull origin main

# Build and deploy
docker-compose down
docker-compose up -d --build

# Wait for services to start
sleep 10

# Check status
docker-compose ps

# Show logs
docker-compose logs -f --tail=50
```

Make it executable:

```bash
chmod +x deploy.sh
```

---

## 🔧 Automated Deployment Script

I'll create a script you can run from your local machine:

### deploy-to-vm.sh

```bash
#!/bin/bash

# Configuration
VM_IP="YOUR_VM_IP"  # Replace with your VM IP
SSH_KEY="/teamspace/studios/this_studio/VM Key.pem"
VM_USER="ubuntu"
DOMAIN="carbonscope.ensimu.space"

echo "🚀 Deploying CarbonScope to VM"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "VM: $VM_IP"
echo "Domain: $DOMAIN"
echo ""

# 1. Upload application files
echo "📦 Uploading application files..."
rsync -avz --exclude 'node_modules' --exclude '.next' --exclude '.git' \
    -e "ssh -i $SSH_KEY" \
    ./apps/ "$VM_USER@$VM_IP:~/carbonscope/"

rsync -avz --exclude '.venv' --exclude '__pycache__' \
    -e "ssh -i $SSH_KEY" \
    ./backend/ "$VM_USER@$VM_IP:~/carbonscope/backend/"

# 2. Upload Docker configs
echo "🐳 Uploading Docker configurations..."
scp -i "$SSH_KEY" docker-compose.yml "$VM_USER@$VM_IP:~/carbonscope/"
scp -i "$SSH_KEY" .env "$VM_USER@$VM_IP:~/carbonscope/"

# 3. Upload Nginx config
echo "⚙️  Uploading Nginx configuration..."
ssh -i "$SSH_KEY" "$VM_USER@$VM_IP" "mkdir -p ~/carbonscope/nginx"
scp -i "$SSH_KEY" nginx/nginx.conf "$VM_USER@$VM_IP:~/carbonscope/nginx/"

# 4. Deploy
echo "🚢 Starting deployment..."
ssh -i "$SSH_KEY" "$VM_USER@$VM_IP" << 'ENDSSH'
cd ~/carbonscope
docker-compose down
docker-compose up -d --build
docker-compose ps
ENDSSH

echo ""
echo "✅ Deployment complete!"
echo "🌐 Visit: https://carbonscope.ensimu.space"
echo ""
```

---

## 🔐 Cloudflare SSL Setup

### Option 1: Cloudflare Flexible SSL (Easiest)

1. Cloudflare handles SSL
2. Connection: Browser → Cloudflare (HTTPS) → VM (HTTP)
3. No SSL certificate needed on VM
4. Works immediately

**Nginx config:** Remove SSL lines, listen on port 80 only

### Option 2: Cloudflare Full SSL (Recommended)

1. Cloudflare generates origin certificate
2. Connection: Browser → Cloudflare (HTTPS) → VM (HTTPS)
3. More secure

**Steps:**
1. Cloudflare Dashboard → SSL/TLS → Origin Server
2. Click "Create Certificate"
3. Copy certificate and private key
4. Save on VM:

```bash
ssh -i "/teamspace/studios/this_studio/VM Key.pem" ubuntu@YOUR_VM_IP

mkdir -p ~/carbonscope/nginx/ssl
nano ~/carbonscope/nginx/ssl/cert.pem  # Paste certificate
nano ~/carbonscope/nginx/ssl/key.pem   # Paste private key
chmod 600 ~/carbonscope/nginx/ssl/key.pem
```

---

## 🧪 Testing Deployment

```bash
# Test HTTP (should redirect to HTTPS)
curl -I http://carbonscope.ensimu.space

# Test HTTPS
curl -I https://carbonscope.ensimu.space

# Test Backend API
curl https://carbonscope.ensimu.space/api/health

# Check Docker containers
ssh -i "/teamspace/studios/this_studio/VM Key.pem" ubuntu@YOUR_VM_IP
docker-compose ps
docker-compose logs -f
```

---

## 📊 Monitoring

### View Logs

```bash
# All services
docker-compose logs -f

# Frontend only
docker-compose logs -f frontend

# Backend only
docker-compose logs -f backend

# Nginx only
docker-compose logs -f nginx
```

### Check Resource Usage

```bash
# Container stats
docker stats

# System resources
htop  # or: top
```

---

## 🔄 Update Deployment

```bash
# SSH into VM
ssh -i "/teamspace/studios/this_studio/VM Key.pem" ubuntu@YOUR_VM_IP

# Pull latest changes
cd ~/carbonscope
git pull

# Rebuild and restart
docker-compose up -d --build

# Check status
docker-compose ps
```

---

## 💰 Cost Estimate

### VM Hosting

| Provider | Specs | Monthly Cost |
|----------|-------|--------------|
| **DigitalOcean** | 2 vCPU, 4GB RAM | $24/month |
| **Linode** | 2 vCPU, 4GB RAM | $24/month |
| **Vultr** | 2 vCPU, 4GB RAM | $24/month |
| **AWS EC2** | t3.medium | ~$30/month |
| **Azure VM** | B2s | ~$30/month |

### Services

| Service | Cost |
|---------|------|
| VM Hosting | $24-30/month |
| Cloudflare DNS | $0 (Free) |
| Cloudflare SSL | $0 (Free) |
| Neon PostgreSQL | $0 (Free tier) |
| Upstash Redis | $0 (Free tier) |
| **TOTAL** | **$24-30/month** |

---

## 🆘 Troubleshooting

### Issue: Can't connect to VM

```bash
# Check VM IP
ping YOUR_VM_IP

# Check SSH key permissions
chmod 600 "/teamspace/studios/this_studio/VM Key.pem"

# Try verbose SSH
ssh -v -i "/teamspace/studios/this_studio/VM Key.pem" ubuntu@YOUR_VM_IP
```

### Issue: Domain not resolving

```bash
# Check DNS propagation
dig carbonscope.ensimu.space

# Check Cloudflare proxy status
# Should show Cloudflare IP, not your VM IP
```

### Issue: Containers not starting

```bash
# Check Docker logs
docker-compose logs

# Check individual container
docker logs carbonscope-frontend

# Restart all containers
docker-compose restart
```

### Issue: 502 Bad Gateway

```bash
# Check backend is running
docker-compose ps
curl http://localhost:8000/health

# Check Nginx config
docker-compose exec nginx nginx -t

# Restart Nginx
docker-compose restart nginx
```

---

## 📝 Checklist

Before deployment:

- [ ] VM IP address obtained
- [ ] SSH access working
- [ ] Docker installed on VM
- [ ] Cloudflare DNS configured
- [ ] SSL/TLS settings configured
- [ ] Environment variables set
- [ ] OAuth credentials obtained
- [ ] Database URL configured

After deployment:

- [ ] Application accessible at https://carbonscope.ensimu.space
- [ ] HTTP redirects to HTTPS
- [ ] Backend API responding
- [ ] Frontend loading correctly
- [ ] Authentication working
- [ ] Docker containers running
- [ ] Logs showing no errors

---

## 🚀 Next Steps

1. **Get your VM IP address**
2. **Configure Cloudflare DNS** (A record pointing to VM)
3. **Run deployment script** from this directory
4. **Test the application**
5. **Set up monitoring** (optional)
6. **Configure backups** (optional)

---

**Questions?**
- Check VM logs: `docker-compose logs -f`
- Test connectivity: `curl -I https://carbonscope.ensimu.space`
- Check DNS: `dig carbonscope.ensimu.space`

**Ready to deploy?** Run: `./deploy-to-vm.sh`
