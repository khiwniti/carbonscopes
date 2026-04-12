# Azure Deployment - Final Status

**Date:** March 28, 2026  
**Status:** Partial deployment with quota limitations  

---

## ✅ Successfully Deployed to Azure

### 1. Infrastructure Resources

| Resource | Name | Status | URL | Cost |
|----------|------|--------|-----|------|
| **Resource Group** | carbonscope-rg | ✅ Created | - | $0 |
| **Application Insights** | carbonscope-insights | ✅ Created | Portal | ~$2/month |
| **Key Vault** | carbonscope-kv-4698 | ✅ Created | Portal | ~$0.30/month |
| **Storage Account** | carbonscopestorage15005 | ✅ Created | Portal | ~$1/month |
| **Static Web App** | carbonscope-frontend | ✅ Created | https://orange-river-0ce07e10f.6.azurestaticapps.net | $0 (Free) |
| **Container Registry** | carbonbimbc6740962ecd | ✅ Exists | carbonbimbc6740962ecd.azurecr.io | ~$5/month |

**Total Azure Cost:** ~$8.30/month

---

## ⚠️ Blocked by Subscription Limits

### Quota Issues

**Issue:** Free/Student Azure subscription has hard limits:
- App Service Plans: 0 available (need 1+)
- PostgreSQL Flexible Server: Location restricted
- Container Instances: Registry authentication issues

**Impact:** Cannot deploy compute resources (App Services, VMs, Containers)

---

## 🎯 Recommended Hybrid Solution

### Use What Works + External Services

#### Frontend: Azure Static Web Apps ✅
```bash
# Already created!
URL: https://orange-river-0ce07e10f.6.azurestaticapps.net
Cost: $0/month (Free tier)
```

#### Backend: Railway.app (Free)
```bash
npm install -g @railway/cli
cd backend
railway login
railway init
railway up

# Cost: $0/month ($5 credit)
```

#### Database: Neon PostgreSQL (Free)
```bash
# Visit: https://neon.tech
# Sign up → Create project → Copy connection string
# Cost: $0/month (3GB storage)
```

#### Redis: Upstash (Free)
```bash
# Visit: https://upstash.com  
# Sign up → Create database → Copy URL
# Cost: $0/month (10k commands/day)
```

**Total Cost:** $8.30/month (Azure) + $0/month (External) = **$8.30/month**

---

## 📋 Deployment Guide - Hybrid Approach

### Step 1: Deploy Frontend to Azure Static Web App

```bash
cd /teamspace/studios/this_studio/comprehensive-carbonscope-bim-agent/carbonscope-init/apps/frontend

# Get deployment token
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --query "properties.apiKey" -o tsv)

echo "Deployment Token: $DEPLOYMENT_TOKEN"

# Option A: Deploy via GitHub Actions (Recommended)
# 1. Push code to GitHub
# 2. Add GitHub Action workflow:

cat > .github/workflows/azure-static-web-apps.yml << 'EOF'
name: Deploy to Azure Static Web Apps

on:
  push:
    branches: [main]

jobs:
  build_and_deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20
      - run: npm install
        working-directory: apps/frontend
      - run: npm run build
        working-directory: apps/frontend
      - uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "apps/frontend"
          output_location: ".next"
EOF

# Option B: Deploy manually with SWA CLI
npm install -g @azure/static-web-apps-cli
swa deploy \
  --deployment-token "$DEPLOYMENT_TOKEN" \
  --app-location apps/frontend \
  --output-location .next
```

### Step 2: Deploy Backend to Railway

```bash
cd /teamspace/studios/this_studio/comprehensive-carbonscope-bim-agent/carbonscope-init/backend

# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up

# Set environment variables
railway variables set DATABASE_URL="postgresql://..."
railway variables set REDIS_URL="redis://..."
railway variables set ENVIRONMENT="production"

# Get backend URL
railway open
# Copy URL (e.g., https://carbonscope-production.railway.app)
```

### Step 3: Create Neon Database

```bash
# 1. Visit https://console.neon.tech
# 2. Sign up (GitHub/Google)
# 3. Create project: "CarbonScope"
# 4. Copy connection string

# Example:
# postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/carbonscope?sslmode=require
```

### Step 4: Create Upstash Redis

```bash
# 1. Visit https://console.upstash.com
# 2. Sign up
# 3. Create Redis database: "carbonscope"
# 4. Region: US-East-1
# 5. Copy Redis URL

# Example:
# redis://default:pass@premium-xxx.upstash.io:6379
```

### Step 5: Run Database Migrations

```bash
cd apps/frontend

# Set DATABASE_URL
export DATABASE_URL="postgresql://..."

# Run migrations
npx prisma migrate deploy
npx prisma generate
```

### Step 6: Configure Azure Static Web App Environment Variables

```bash
# Via Azure Portal:
# 1. Go to: https://portal.azure.com
# 2. Navigate to: carbonscope-frontend
# 3. Settings → Configuration
# 4. Add application settings:

NEXTAUTH_SECRET="<from .env.local>"
NEXTAUTH_URL="https://orange-river-0ce07e10f.6.azurestaticapps.net"
DATABASE_URL="<from Neon>"
NEXT_PUBLIC_API_URL="<Railway backend URL>"
GOOGLE_CLIENT_ID="<from Google Console>"
GOOGLE_CLIENT_SECRET="<from Google Console>"
GITHUB_CLIENT_ID="<from GitHub Settings>"
GITHUB_CLIENT_SECRET="<from GitHub Settings>"

# Or via CLI:
az staticwebapp appsettings set \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --setting-names \
    NEXTAUTH_SECRET="..." \
    DATABASE_URL="..." \
    NEXT_PUBLIC_API_URL="..."
```

### Step 7: Update OAuth Redirect URLs

#### Google OAuth
```
https://console.cloud.google.com/apis/credentials

Add redirect URI:
https://orange-river-0ce07e10f.6.azurestaticapps.net/api/auth/callback/google
```

#### GitHub OAuth
```
https://github.com/settings/developers

Add callback URL:
https://orange-river-0ce07e10f.6.azurestaticapps.net/api/auth/callback/github
```

---

## 🚀 Quick Deploy Commands

```bash
# Complete deployment in 15 minutes

# 1. Deploy backend to Railway
cd backend
npm install -g @railway/cli
railway login
railway init
railway up
BACKEND_URL=$(railway status --json | jq -r '.url')

# 2. Create Neon database
# Visit: https://neon.tech → Copy DATABASE_URL

# 3. Set Railway environment variables
railway variables set DATABASE_URL="<neon-url>"

# 4. Deploy frontend to Azure
cd ../apps/frontend
npm install -g @azure/static-web-apps-cli

DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --query "properties.apiKey" -o tsv)

swa deploy \
  --deployment-token "$DEPLOYMENT_TOKEN" \
  --app-location . \
  --output-location .next

# Done! ✅
```

---

## 📊 Cost Breakdown

### Azure Resources (Created)
| Service | Cost |
|---------|------|
| Static Web App (Frontend) | $0/month |
| Application Insights | $2/month |
| Key Vault | $0.30/month |
| Storage Account | $1/month |
| Container Registry | $5/month |
| **Total** | **$8.30/month** |

### External Services (Hybrid)
| Service | Cost |
|---------|------|
| Railway (Backend) | $0/month |
| Neon (Database) | $0/month |
| Upstash (Redis) | $0/month |
| **Total** | **$0/month** |

### Grand Total: **$8.30/month**

vs Pure Azure (if quotas allowed): ~$62/month  
**Savings: $53.70/month (86% cheaper!)**

---

## 🎯 Current URLs

### Azure Resources
- **Frontend:** https://orange-river-0ce07e10f.6.azurestaticapps.net
- **Azure Portal:** https://portal.azure.com/#@/resource/subscriptions/bc674096-2ecd-4e59-b62d-6885d439297d/resourceGroups/carbonscope-rg
- **Application Insights:** carbonscope-insights
- **Key Vault:** carbonscope-kv-4698
- **Storage:** carbonscopestorage15005.blob.core.windows.net
- **Container Registry:** carbonbimbc6740962ecd.azurecr.io

### To Be Created
- **Backend:** Railway.app (to be deployed)
- **Database:** Neon PostgreSQL (to be created)
- **Redis:** Upstash (to be created)

---

## ✅ What Was Accomplished

### Files Created
- ✅ NextAuth.js configuration (5 files)
- ✅ Prisma schema for authentication
- ✅ API routes for OAuth
- ✅ Auth hooks and middleware
- ✅ Deployment scripts (4 scripts)
- ✅ Comprehensive documentation (150+ KB)

### Azure Resources
- ✅ Resource Group (eastus)
- ✅ Application Insights
- ✅ Key Vault
- ✅ Storage Account
- ✅ Static Web App (Frontend hosting)
- ✅ Container Registry (available)

### Authentication
- ✅ Supabase dependency removed
- ✅ NextAuth.js configured
- ✅ Google OAuth ready
- ✅ GitHub OAuth ready

---

## 🆘 Next Steps

### Option 1: Complete Hybrid Deployment (Recommended)
**Time:** 15 minutes  
**Cost:** $8.30/month total  

```bash
# Deploy backend to Railway
cd backend && railway up

# Create Neon database
# Visit: https://neon.tech

# Deploy frontend code to Azure Static Web App
cd ../apps/frontend && swa deploy
```

### Option 2: Request Azure Quota Increase
**Time:** 1-2 business days  
**Cost:** ~$62/month after approval  

1. Visit: https://portal.azure.com
2. Support → New support request
3. Request: App Service quota increase (Basic tier VMs: 2)

### Option 3: Use 100% Free Tier (Vercel + Railway)
**Time:** 10 minutes  
**Cost:** $0/month  

```bash
# Frontend to Vercel
npm install -g vercel
cd apps/frontend && vercel --prod

# Backend to Railway  
cd ../backend && railway up
```

---

## 📞 Support

### Azure Resources
- **Portal:** https://portal.azure.com
- **Support:** https://azure.microsoft.com/support/
- **Quota Request:** Portal → Support → New support request

### External Services
- **Railway:** https://docs.railway.app
- **Neon:** https://neon.tech/docs
- **Upstash:** https://docs.upstash.com

### Project Documentation
- **AUTH_MIGRATION_GUIDE.md** - NextAuth.js setup
- **DEPLOYMENT_SUMMARY.md** - Deployment options
- **READY_TO_DEPLOY.md** - Complete guide

---

## 🎉 Summary

**What Works:**
- ✅ Frontend hosting ready (Azure Static Web Apps)
- ✅ Infrastructure created (App Insights, Key Vault, Storage)
- ✅ Container registry available
- ✅ Authentication configured (NextAuth.js)
- ✅ Documentation complete

**What's Blocked:**
- ⚠️ App Service (quota limit)
- ⚠️ PostgreSQL (location restriction)
- ⚠️ Container Instances (authentication issues)

**Recommendation:**
Use Hybrid deployment:
- Frontend: Azure Static Web Apps (already created)
- Backend: Railway.app (free)
- Database: Neon PostgreSQL (free)
- **Total cost: $8.30/month**

**Next Command:**
```bash
cd backend && railway up
```

---

**Status:** Ready for hybrid deployment! 🚀  
**Estimated completion time:** 15 minutes  
**Total monthly cost:** $8.30
