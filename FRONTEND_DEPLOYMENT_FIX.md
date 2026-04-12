# Frontend Deployment Fix Guide

**Date:** March 29, 2026
**Issue:** Frontend created but never deployed to Azure Static Web Apps
**Backend:** ✅ Working at https://carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io

---

## 🔧 Step 1: Fix Configuration Issues

### A. Update next.config.ts Backend URL

Replace the old CarbonScope URLs with the Azure backend:

```typescript
// apps/frontend/next.config.ts
const getBackendUrl = (): string => {
  // Check both variable names for compatibility
  const explicitUrl = process.env.NEXT_PUBLIC_BACKEND_URL || process.env.NEXT_PUBLIC_API_URL;
  if (explicitUrl && explicitUrl.trim() !== '') {
    return explicitUrl;
  }

  // Azure Container Apps backend (production)
  return 'https://carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io';
};
```

### B. Update .env.production

Standardize the variable name:

```bash
# apps/frontend/.env.production
NEXT_PUBLIC_BACKEND_URL=https://carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io

# Static Web App Configuration
NEXTAUTH_URL=https://orange-river-0ce07e10f.6.azurestaticapps.net
NEXTAUTH_SECRET=gQAd7q+qZ8THFpLjmLdwx7VxhMPOKfU8W3zQkRbN2Ys=

# Database (configure later)
DATABASE_URL=postgresql://placeholder:placeholder@localhost/placeholder
```

---

## 🚀 Step 2: Deploy to Azure Static Web Apps

### Method A: Using SWA CLI (Recommended)

```bash
# 1. Get deployment token from Azure
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --query "properties.apiKey" -o tsv)

# 2. Navigate to frontend
cd /teamspace/studios/this_studio/comprehensive-carbonscope-bim-agent/carbonscope-init/apps/frontend

# 3. Build the application
pnpm build

# 4. Install SWA CLI globally
npm install -g @azure/static-web-apps-cli

# 5. Deploy
swa deploy \
  --deployment-token "$DEPLOYMENT_TOKEN" \
  --app-location . \
  --output-location .next

# Expected output:
# ✓ Deployment successful
# ✓ Frontend available at: https://orange-river-0ce07e10f.6.azurestaticapps.net
```

### Method B: Using GitHub Actions (Automated)

Create `.github/workflows/azure-static-web-apps.yml`:

```yaml
name: Azure Static Web Apps CI/CD

on:
  push:
    branches:
      - main
    paths:
      - 'apps/frontend/**'
  pull_request:
    types: [opened, synchronize, reopened, closed]
    branches:
      - main

jobs:
  build_and_deploy_job:
    if: github.event_name == 'push' || (github.event_name == 'pull_request' && github.event.action != 'closed')
    runs-on: ubuntu-latest
    name: Build and Deploy Job
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: true

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Build And Deploy
        id: builddeploy
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "apps/frontend"
          output_location: ".next"

  close_pull_request_job:
    if: github.event_name == 'pull_request' && github.event.action == 'closed'
    runs-on: ubuntu-latest
    name: Close Pull Request Job
    steps:
      - name: Close Pull Request
        id: closepullrequest
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          action: "close"
```

Then add the deployment token as a GitHub secret:

```bash
# Get the token
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --query "properties.apiKey" -o tsv)

# Add to GitHub secrets via CLI or dashboard
gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN --body "$DEPLOYMENT_TOKEN"
```

---

## 🔍 Step 3: Verify Deployment

```bash
# 1. Check Static Web App status
az staticwebapp show \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg

# 2. Test the frontend URL
curl -I https://orange-river-0ce07e10f.6.azurestaticapps.net

# Expected: HTTP/2 200

# 3. Check if it's calling the correct backend
# Open browser DevTools → Network tab
# Visit: https://orange-river-0ce07e10f.6.azurestaticapps.net
# Check API calls go to: https://carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io
```

---

## 🎯 Alternative: Deploy to Azure Container Apps

If you prefer to deploy the frontend as a container (not recommended, more expensive):

```bash
# 1. Build Docker image from monorepo root
cd /teamspace/studios/this_studio/comprehensive-carbonscope-bim-agent/carbonscope-init
docker build -f apps/frontend/Dockerfile -t carbonbimbc6740962ecd.azurecr.io/carbonscope-frontend:latest .

# 2. Push to ACR
az acr login --name carbonbimbc6740962ecd
docker push carbonbimbc6740962ecd.azurecr.io/carbonscope-frontend:latest

# 3. Deploy to Container Apps
az containerapp create \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --environment carbonscope-env \
  --image carbonbimbc6740962ecd.azurecr.io/carbonscope-frontend:latest \
  --registry-server carbonbimbc6740962ecd.azurecr.io \
  --target-port 3000 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 2 \
  --cpu 0.5 \
  --memory 1Gi \
  --env-vars \
    NEXT_PUBLIC_BACKEND_URL=https://carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io

# Note: This adds ~$10-15/month to your costs
```

---

## 📊 Cost Comparison

| Deployment Method | Monthly Cost | Pros | Cons |
|-------------------|--------------|------|------|
| **Static Web Apps** (Recommended) | **$0** (Free tier) | • Free<br>• Global CDN<br>• Auto-SSL<br>• Perfect for Next.js | • Static only (SSG/SSR via functions) |
| Container Apps | $10-15 | • Full Node.js runtime<br>• More flexibility | • Costs money<br>• Overkill for static frontend |

---

## ✅ Post-Deployment Checklist

After deployment, verify:

- [ ] Frontend loads at Azure Static Web Apps URL
- [ ] API calls reach Azure Container Apps backend
- [ ] Authentication flows work (NextAuth)
- [ ] Environment variables are set correctly
- [ ] No CORS errors in browser console
- [ ] Static assets (images, fonts) load correctly
- [ ] Responsive design works across devices

---

## 🔧 Troubleshooting

### Frontend Shows 404

```bash
# Check deployment status
az staticwebapp show \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --query "defaultHostname" -o tsv

# Verify build output exists
ls -la apps/frontend/.next/
```

### API Calls Fail (CORS)

Add CORS middleware to backend (`backend/api.py`):

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://orange-river-0ce07e10f.6.azurestaticapps.net",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### NextAuth Errors

Verify environment variables:

```bash
# Check Static Web App configuration
az staticwebapp appsettings list \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg

# Set if missing
az staticwebapp appsettings set \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --setting-names \
    NEXTAUTH_URL=https://orange-river-0ce07e10f.6.azurestaticapps.net \
    NEXTAUTH_SECRET=gQAd7q+qZ8THFpLjmLdwx7VxhMPOKfU8W3zQkRbN2Ys=
```

---

## 🎉 Summary

### Root Cause
1. Pi agent created Azure Static Web App but never executed deployment
2. Configuration had environment variable name mismatch
3. Old CarbonScope URLs in next.config.ts instead of Azure backend

### Solution
1. Fix `next.config.ts` to use Azure backend URL
2. Standardize env var to `NEXT_PUBLIC_BACKEND_URL`
3. Deploy using SWA CLI or GitHub Actions
4. Verify frontend connects to backend correctly

### Expected Outcome
- Frontend: https://orange-river-0ce07e10f.6.azurestaticapps.net
- Backend: https://carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io
- Total Cost: **$18-33/month** (backend only, frontend free)

---

**Next Step:** Choose deployment method and execute Step 2 commands.
