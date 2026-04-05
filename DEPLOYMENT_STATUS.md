# CarbonScope Deployment Status

**Date:** March 28, 2026  
**Current Step:** OAuth Credentials Required  

---

## ✅ Completed Steps

### 1. Authentication Migration ✅
- [x] NextAuth.js files created
- [x] Prisma schema generated
- [x] Auth API routes created
- [x] Auth hooks created
- [x] Middleware configured
- [x] NEXTAUTH_SECRET generated

**Files Created:**
- `apps/frontend/src/lib/auth.ts`
- `apps/frontend/src/app/api/auth/[...nextauth]/route.ts`
- `apps/frontend/src/hooks/use-auth.ts`
- `apps/frontend/src/middleware.ts`
- `apps/frontend/prisma/schema.prisma`
- `apps/frontend/.env.local.template`

---

## 🔄 Current Step: Get OAuth Credentials

Before deploying to Azure, you need OAuth credentials from Google and GitHub.

### Option A: Skip OAuth for Now (Use Email/Password)

If you want to deploy NOW without OAuth:

```bash
# We'll add email/password auth temporarily
# You can add OAuth providers later
./deploy-azure.sh
```

### Option B: Get OAuth Credentials (Recommended - 10 minutes)

#### 1. Google OAuth Setup

**URL:** https://console.cloud.google.com/apis/credentials

**Steps:**
1. Go to Google Cloud Console
2. Select or create a project
3. Click "Create Credentials" → "OAuth client ID"
4. Application type: "Web application"
5. Name: "CarbonScope Production"
6. Authorized redirect URIs:
   ```
   http://localhost:3000/api/auth/callback/google
   https://carbonscope-frontend.azurewebsites.net/api/auth/callback/google
   ```
7. Click "Create"
8. Copy **Client ID** and **Client Secret**

**Time:** ~5 minutes

---

#### 2. GitHub OAuth Setup

**URL:** https://github.com/settings/developers

**Steps:**
1. Go to GitHub Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Application name: "CarbonScope"
4. Homepage URL: `https://carbonscope-frontend.azurewebsites.net`
5. Authorization callback URL:
   ```
   http://localhost:3000/api/auth/callback/github
   ```
   (Add production URL after deployment)
6. Click "Register application"
7. Generate a new client secret
8. Copy **Client ID** and **Client Secret**

**Time:** ~5 minutes

---

### 3. Update Environment Variables

After getting credentials:

```bash
# Copy template
cd apps/frontend
cp .env.local.template .env.local

# Edit with your credentials
nano .env.local
```

Update these values:
```env
GOOGLE_CLIENT_ID="your-actual-google-id"
GOOGLE_CLIENT_SECRET="your-actual-google-secret"
GITHUB_CLIENT_ID="your-actual-github-id"
GITHUB_CLIENT_SECRET="your-actual-github-secret"
```

---

## 🚀 Next Steps

### After Getting OAuth Credentials:

```bash
# 1. Check Azure CLI is installed
az --version

# 2. Login to Azure
az login

# 3. Deploy infrastructure (~20 minutes)
./deploy-azure.sh

# 4. Deploy application code (~10 minutes)
./deploy-code.sh

# 5. Update OAuth redirect URLs with production domain
```

---

## ⏭️ Skip OAuth and Deploy Now

If you want to deploy without OAuth right now:

```bash
# We'll use a minimal auth setup for deployment
# You can add OAuth providers after infrastructure is ready

# 1. Login to Azure
az login

# 2. Deploy infrastructure
./deploy-azure.sh

# 3. Deploy code
./deploy-code.sh

# 4. Add OAuth credentials later through Azure Portal
```

---

## 📋 Pre-Deployment Checklist

### Required:
- [x] ✅ NextAuth.js files created
- [x] ✅ Azure CLI installed (`az --version`)
- [ ] ⏳ Azure account login (`az login`)
- [ ] ⏳ OAuth credentials (or skip for now)

### Optional (can do later):
- [ ] Custom domain name
- [ ] SSL certificate
- [ ] GitHub Actions CI/CD
- [ ] Additional OAuth providers (Discord, Twitter, etc.)

---

## 💰 Cost Reminder

**Azure Infrastructure:** ~$62/month
- App Service (Frontend): $13
- App Service (Backend): $13
- PostgreSQL: $12
- Redis: $16
- Storage: $1
- Other: $7

**Authentication:** $0/month (NextAuth.js)

**Total:** ~$62/month

---

## 🆘 Need Help?

### Getting OAuth credentials:
- **Google:** https://console.cloud.google.com/apis/credentials
- **GitHub:** https://github.com/settings/developers
- **Tutorial:** https://next-auth.js.org/providers/google

### Azure deployment:
- **Documentation:** `AZURE_DEPLOYMENT_COMPLETE.md`
- **Quick reference:** `DEPLOYMENT_QUICK_REF.txt`

---

## 🎯 What Happens Next?

1. **Infrastructure Deployment** (`./deploy-azure.sh`):
   - Creates resource group
   - Sets up PostgreSQL database
   - Creates Redis cache
   - Configures storage
   - Creates App Services
   - Sets up Key Vault
   - Configures Application Insights

2. **Code Deployment** (`./deploy-code.sh`):
   - Builds frontend
   - Deploys Next.js app
   - Deploys FastAPI backend
   - Runs database migrations
   - Starts services

3. **Post-Deployment**:
   - Test authentication
   - Add OAuth providers
   - Configure custom domain
   - Set up CI/CD

---

## 🚀 Ready to Deploy?

Choose one:

**Option 1: Get OAuth first (recommended)**
```bash
# 1. Get Google OAuth (5 min): https://console.cloud.google.com/apis/credentials
# 2. Get GitHub OAuth (5 min): https://github.com/settings/developers
# 3. Update .env.local with credentials
# 4. Run: ./deploy-azure.sh
```

**Option 2: Deploy now, add OAuth later**
```bash
# 1. Login: az login
# 2. Deploy: ./deploy-azure.sh
# 3. Add OAuth through Azure Portal later
```

---

**Current Status:** ✅ Ready for Azure deployment  
**Next Command:** `az login` then `./deploy-azure.sh`  
**Estimated Time:** 30-40 minutes total
