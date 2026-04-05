# CarbonScope Azure Deployment - Complete Guide

**Date:** March 28, 2026  
**Status:** Ready to Deploy  

---

## 🎯 Overview

Complete Azure deployment solution for **CarbonScope** (formerly CarbonScope) with **NextAuth.js authentication** (no Supabase dependency).

---

## 📦 What's Included

### 1. **Infrastructure Deployment** (`deploy-azure.sh`)
- ✅ Resource Group
- ✅ PostgreSQL Flexible Server (B1ms)
- ✅ Redis Cache (Basic C0)
- ✅ Storage Account (Blob storage)
- ✅ App Services (Frontend + Backend)
- ✅ Key Vault (Secret management)
- ✅ Application Insights (Monitoring)
- ✅ Managed Identity (Secure access)

### 2. **Code Deployment** (`deploy-code.sh`)
- ✅ Frontend (Next.js 15) deployment
- ✅ Backend (FastAPI) deployment
- ✅ Automatic builds
- ✅ Environment configuration
- ✅ Health checks

### 3. **Authentication Migration** (`migrate-auth.sh`)
- ✅ NextAuth.js setup
- ✅ Google OAuth integration
- ✅ GitHub OAuth integration
- ✅ Database session storage
- ✅ Route protection middleware

### 4. **Documentation**
- ✅ `AUTH_MIGRATION_GUIDE.md` (19 KB) - Complete auth migration guide
- ✅ `CLOUD_MIGRATION_SUMMARY.md` (12 KB) - Database options
- ✅ `DATABASE_MIGRATION_GUIDE.md` (12 KB) - PostgreSQL setup
- ✅ `GRAPH_DATABASE_MIGRATION.md` (16 KB) - Neo4j for BIM data

---

## 🚀 Quick Start (3 Commands)

### Option A: Full Automated Deployment

```bash
# 1. Deploy Azure infrastructure
./deploy-azure.sh

# 2. Migrate authentication (removes Supabase dependency)
./migrate-auth.sh

# 3. Deploy application code
./deploy-code.sh
```

**Total time:** ~30 minutes  
**Cost:** ~$57/month (all services)

---

### Option B: Step-by-Step (Recommended for First Time)

#### Step 1: Authentication Migration (Local First)

```bash
# Run migration script
./migrate-auth.sh

# Follow prompts to:
# - Install NextAuth.js
# - Create Prisma schema
# - Generate auth files
# - Get NEXTAUTH_SECRET

# Get OAuth credentials:
# Google: https://console.cloud.google.com/apis/credentials
# GitHub: https://github.com/settings/developers

# Update .env.local with credentials
nano apps/frontend/.env.local

# Run migrations
cd apps/frontend
npx prisma migrate dev --name add_auth_tables
npx prisma generate

# Test locally
pnpm dev
# Visit: http://localhost:3000/auth
```

#### Step 2: Deploy Infrastructure

```bash
# Login to Azure
az login

# Deploy infrastructure (interactive)
./deploy-azure.sh

# Note the output URLs:
# - Frontend: https://carbonscope-frontend.azurewebsites.net
# - Backend: https://carbonscope-backend.azurewebsites.net
# - Database: carbonscope-postgres.postgres.database.azure.com
```

#### Step 3: Configure Production OAuth

```bash
# Update OAuth redirect URLs for production:

# Google Console:
# Add: https://carbonscope-frontend.azurewebsites.net/api/auth/callback/google

# GitHub Settings:
# Add: https://carbonscope-frontend.azurewebsites.net/api/auth/callback/github
```

#### Step 4: Set Azure Environment Variables

```bash
# Get your NEXTAUTH_SECRET from local .env
NEXTAUTH_SECRET=$(grep NEXTAUTH_SECRET apps/frontend/.env.local | cut -d '=' -f2)

# Set in Azure
az webapp config appsettings set \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --settings \
    "NEXTAUTH_URL=https://carbonscope-frontend.azurewebsites.net" \
    "NEXTAUTH_SECRET=${NEXTAUTH_SECRET}" \
    "GOOGLE_CLIENT_ID=your-google-id" \
    "GOOGLE_CLIENT_SECRET=your-google-secret" \
    "GITHUB_CLIENT_ID=your-github-id" \
    "GITHUB_CLIENT_SECRET=your-github-secret"
```

#### Step 5: Deploy Code

```bash
# Deploy both frontend and backend
./deploy-code.sh

# Or deploy individually:
# 1) Both
# 2) Frontend only
# 3) Backend only
```

#### Step 6: Verify Deployment

```bash
# Check frontend
curl https://carbonscope-frontend.azurewebsites.net

# Check backend API
curl https://carbonscope-backend.azurewebsites.net/health

# Test authentication
# Visit: https://carbonscope-frontend.azurewebsites.net/auth
```

---

## 💰 Cost Breakdown

### Monthly Costs (Production)

| Service | SKU | Monthly Cost |
|---------|-----|--------------|
| **App Service Plan (Frontend)** | B1 | ~$13 |
| **App Service Plan (Backend)** | B1 | ~$13 |
| **PostgreSQL Flexible Server** | B1ms | ~$12 |
| **Redis Cache** | Basic C0 | ~$16 |
| **Storage Account** | Standard LRS | ~$1 |
| **Application Insights** | Pay-as-you-go | ~$2 |
| **Key Vault** | Standard | ~$0.30 |
| **Data Transfer** | Estimate | ~$5 |
| **TOTAL** | | **~$62/month** |

### Development/Staging (Optional)

- Use **Free tier** for PostgreSQL: $0
- Use **Free tier** for App Services: $0
- Use **Upstash Redis** (free): $0
- **Total Dev Cost:** ~$0-5/month

### Comparison to Supabase

| Stack | Monthly Cost |
|-------|--------------|
| **Azure + NextAuth.js** | $62 |
| **Supabase (paid tier)** | $25 + auth costs |
| **Savings with NextAuth** | **$0 auth costs** |

---

## 🔐 Authentication: NextAuth.js vs Supabase

### Why NextAuth.js?

| Feature | NextAuth.js | Supabase Auth |
|---------|-------------|---------------|
| **Cost** | $0/month | $25+/month |
| **Self-hosted** | ✅ Yes | ❌ No |
| **Providers** | 50+ | 10+ |
| **Database** | Your PostgreSQL | Supabase only |
| **Customization** | Full control | Limited |
| **Next.js integration** | Native | Requires SDK |
| **TypeScript** | ✅ First-class | ✅ Good |
| **Session strategy** | Database or JWT | JWT only |
| **Vendor lock-in** | ❌ None | ⚠️ High |

### Migration Impact

**Before (Supabase Auth):**
```typescript
import { createClient } from '@supabase/supabase-js';
const supabase = createClient(url, key);
await supabase.auth.signInWithOAuth({ provider: 'google' });
```

**After (NextAuth.js):**
```typescript
import { signIn } from 'next-auth/react';
await signIn('google');
```

**Simpler, cleaner, no external dependencies!**

---

## 📋 Deployment Checklist

### Pre-Deployment

- [ ] Azure account created
- [ ] Azure CLI installed (`az --version`)
- [ ] Node.js 20+ installed (`node --version`)
- [ ] Python 3.11+ installed (`python --version`)
- [ ] pnpm installed (`pnpm --version`)
- [ ] Git repository up to date

### OAuth Setup

- [ ] Google OAuth credentials obtained
- [ ] GitHub OAuth credentials obtained
- [ ] Redirect URLs configured (local + production)
- [ ] NEXTAUTH_SECRET generated

### Local Testing

- [ ] NextAuth.js installed
- [ ] Prisma migrations run
- [ ] Google sign-in tested locally
- [ ] GitHub sign-in tested locally
- [ ] Protected routes working
- [ ] Session persistence verified

### Azure Infrastructure

- [ ] Resource group created
- [ ] PostgreSQL server provisioned
- [ ] Redis cache created
- [ ] Storage account set up
- [ ] App Services created
- [ ] Key Vault configured
- [ ] Managed Identity enabled

### Environment Variables

- [ ] Local .env.local configured
- [ ] Azure frontend app settings configured
- [ ] Azure backend app settings configured
- [ ] Database URL set in Key Vault
- [ ] OAuth secrets set
- [ ] NEXTAUTH_SECRET set

### Code Deployment

- [ ] Frontend built successfully
- [ ] Backend dependencies installed
- [ ] Frontend deployed to Azure
- [ ] Backend deployed to Azure
- [ ] Apps restarted

### Production Testing

- [ ] Frontend URL accessible
- [ ] Backend API responding
- [ ] Google sign-in working
- [ ] GitHub sign-in working
- [ ] Dashboard accessible after auth
- [ ] Session persistence verified
- [ ] Logout working

### Monitoring

- [ ] Application Insights collecting data
- [ ] Log streams configured
- [ ] Alerts set up (optional)
- [ ] Error tracking enabled

### DNS & SSL (Optional)

- [ ] Custom domain configured
- [ ] SSL certificate installed
- [ ] HTTPS redirect enabled
- [ ] OAuth redirect URLs updated

---

## 🛠 Useful Commands

### Azure Management

```bash
# Login
az login

# List resources
az resource list --resource-group carbonscope-rg --output table

# View app logs (real-time)
az webapp log tail --name carbonscope-frontend --resource-group carbonscope-rg

# Restart app
az webapp restart --name carbonscope-frontend --resource-group carbonscope-rg

# SSH into app
az webapp ssh --name carbonscope-frontend --resource-group carbonscope-rg

# View environment variables
az webapp config appsettings list --name carbonscope-frontend --resource-group carbonscope-rg

# Update environment variable
az webapp config appsettings set \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --settings KEY=VALUE
```

### Database Management

```bash
# Connect to PostgreSQL
psql "host=carbonscope-postgres.postgres.database.azure.com \
      port=5432 \
      dbname=carbonscope_db \
      user=carbonscope_admin \
      sslmode=require"

# Run Prisma migrations
cd apps/frontend
npx prisma migrate deploy

# View database
npx prisma studio
```

### Monitoring

```bash
# View Application Insights metrics
az monitor app-insights component show \
  --app carbonscope-insights \
  --resource-group carbonscope-rg

# Query logs
az monitor app-insights query \
  --app carbonscope-insights \
  --analytics-query "requests | where timestamp > ago(1h)"
```

---

## 🐛 Troubleshooting

### Issue: "OAuth callback URL mismatch"

**Solution:**
```bash
# Check redirect URLs match exactly
# Google Console: https://console.cloud.google.com/apis/credentials
# GitHub Settings: https://github.com/settings/developers

# URLs must match exactly (http vs https, trailing slash)
# ✅ Correct: https://carbonscope-frontend.azurewebsites.net/api/auth/callback/google
# ❌ Wrong: http://carbonscope-frontend.azurewebsites.net/api/auth/callback/google
```

### Issue: "Database connection failed"

**Solution:**
```bash
# Check DATABASE_URL format
postgresql://user:password@host:5432/database?sslmode=require

# Verify firewall rules allow Azure services
az postgres flexible-server firewall-rule create \
  --resource-group carbonscope-rg \
  --name carbonscope-postgres \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### Issue: "Session not persisting"

**Solution:**
```bash
# Check Prisma is configured correctly
cd apps/frontend
npx prisma generate

# Verify session table exists
npx prisma studio

# Check NEXTAUTH_SECRET is set in Azure
az webapp config appsettings list \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  | grep NEXTAUTH_SECRET
```

### Issue: "App not starting"

**Solution:**
```bash
# View logs
az webapp log tail --name carbonscope-frontend --resource-group carbonscope-rg

# Check startup command
az webapp config show \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  | grep startupCommand

# Common fixes:
# 1. Ensure Node.js version is 20+
# 2. Check package.json "start" script
# 3. Verify all environment variables are set
```

---

## 🚢 CI/CD with GitHub Actions (Bonus)

Create `.github/workflows/deploy-azure.yml`:

```yaml
name: Deploy to Azure

on:
  push:
    branches: [main]

jobs:
  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: pnpm/action-setup@v2
        with:
          version: 8
      
      - uses: actions/setup-node@v3
        with:
          node-version: 20
          cache: 'pnpm'
      
      - name: Install dependencies
        run: pnpm install --frozen-lockfile
        working-directory: apps/frontend
      
      - name: Build
        run: pnpm build
        working-directory: apps/frontend
      
      - uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy to Azure
        run: |
          cd apps/frontend
          zip -r ../../frontend-deploy.zip .
          az webapp deploy \
            --resource-group carbonscope-rg \
            --name carbonscope-frontend \
            --src-path ../../frontend-deploy.zip \
            --type zip

  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
        working-directory: backend
      
      - uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Deploy to Azure
        run: |
          cd backend
          zip -r ../backend-deploy.zip .
          az webapp deploy \
            --resource-group carbonscope-rg \
            --name carbonscope-backend \
            --src-path ../backend-deploy.zip \
            --type zip
```

---

## 📚 Additional Resources

### NextAuth.js
- **Documentation:** https://authjs.dev
- **Providers:** https://authjs.dev/reference/core/providers
- **Prisma Adapter:** https://authjs.dev/reference/adapter/prisma

### Azure
- **App Service:** https://docs.microsoft.com/azure/app-service/
- **PostgreSQL:** https://docs.microsoft.com/azure/postgresql/
- **Key Vault:** https://docs.microsoft.com/azure/key-vault/

### OAuth Setup
- **Google:** https://console.cloud.google.com/apis/credentials
- **GitHub:** https://github.com/settings/developers

---

## 🎉 Success Criteria

Your deployment is successful when:

- [x] ✅ Frontend accessible at `https://carbonscope-frontend.azurewebsites.net`
- [x] ✅ Backend API responding at `https://carbonscope-backend.azurewebsites.net/docs`
- [x] ✅ Google sign-in works (redirects to dashboard)
- [x] ✅ GitHub sign-in works (redirects to dashboard)
- [x] ✅ Session persists across page refreshes
- [x] ✅ Protected routes require authentication
- [x] ✅ Logout clears session
- [x] ✅ No Supabase dependencies
- [x] ✅ All services running in Azure
- [x] ✅ Application Insights collecting data

---

## 🆘 Support

**Issues?** Check these resources:

1. **Logs:** `az webapp log tail --name carbonscope-frontend --resource-group carbonscope-rg`
2. **Azure Portal:** https://portal.azure.com
3. **NextAuth.js Discord:** https://discord.gg/nextauth
4. **This Documentation:** Read `AUTH_MIGRATION_GUIDE.md` for detailed auth info

---

## 📝 Summary

You now have:

1. ✅ **3 deployment scripts** (infrastructure, code, auth)
2. ✅ **Complete Azure setup** (~$62/month)
3. ✅ **NextAuth.js authentication** ($0/month, no Supabase)
4. ✅ **Production-ready configuration**
5. ✅ **Comprehensive documentation**

**Total Setup Time:** 2-3 hours  
**Monthly Cost:** $57-62 (Azure) + $0 (Auth)  
**Status:** ✅ Ready to deploy!

---

**Created:** March 28, 2026  
**Version:** 1.0.0  
**Next Step:** Run `./migrate-auth.sh` to get started! 🚀
