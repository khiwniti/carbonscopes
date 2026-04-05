# Frontend Direct Deployment (Cloud Build)

**Issue:** Local build runs out of memory during compilation
**Solution:** Deploy source code to Azure Static Web Apps and let Azure build it

---

## ✅ Code Status

All ESLint errors fixed:
- ✅ Navigation links using `<Link>` instead of `<a>`
- ✅ TypeScript comments with proper descriptions
- ✅ Code ready for production build

**Local build fails due to:** Resource constraints (SIGKILL during compilation)
**Solution:** Azure SWA has more build resources

---

## 🚀 Deployment Method: GitHub Actions (Recommended)

Azure Static Web Apps integrates with GitHub Actions for automatic builds.

### Step 1: Push Code to GitHub

```bash
cd /teamspace/studios/this_studio/comprehensive-suna-bim-agent/suna-init

# Commit the fixes
git add apps/frontend/src/app/auth/error.tsx
git add apps/frontend/src/app/error.tsx
git add apps/frontend/src/app/share/[threadId]/page.tsx
git add apps/frontend/src/lib/auth.ts
git add apps/frontend/next.config.ts
git add apps/frontend/.env.production

git commit -m "fix: resolve ESLint errors for production build

- Replace <a> with <Link> for internal navigation
- Add descriptions to @ts-expect-error comments
- Update backend URL configuration for Azure deployment"

git push origin main
```

### Step 2: Configure GitHub Action

Azure Static Web Apps automatically creates a GitHub Action workflow when you connect the repository.

**If not already configured:**

```bash
# Get the deployment token
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --query "properties.apiKey" -o tsv)

# Add as GitHub secret
gh secret set AZURE_STATIC_WEB_APPS_API_TOKEN --body "$DEPLOYMENT_TOKEN"
```

**Workflow file** (`.github/workflows/azure-static-web-apps.yml`):

```yaml
name: Azure Static Web Apps CI/CD

on:
  push:
    branches:
      - main
  pull_request:
    types: [opened, synchronize, reopened, closed]
    branches:
      - main

jobs:
  build_and_deploy_job:
    runs-on: ubuntu-latest
    name: Build and Deploy
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: true

      - name: Setup pnpm
        uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Build And Deploy
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "apps/frontend"
          output_location: ".next"
          app_build_command: "cd ../.. && pnpm install && cd apps/frontend && pnpm build"
```

---

## 🎯 Alternative: Manual CLI Deployment

If you want to try local deployment despite memory constraints:

### Option A: Increase Node Memory

```bash
export NODE_OPTIONS="--max-old-space-size=8192"
cd apps/frontend
pnpm build
```

### Option B: Deploy Without Building

```bash
# Skip local build, let Azure build in the cloud
cd /teamspace/studios/this_studio/comprehensive-suna-bim-agent/suna-init

# Get deployment token
DEPLOYMENT_TOKEN=$(az staticwebapp secrets list \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --query "properties.apiKey" -o tsv)

# Deploy source code (Azure will build it)
cd apps/frontend
npx @azure/static-web-apps-cli deploy \
  --deployment-token "$DEPLOYMENT_TOKEN" \
  --app-location . \
  --skip-app-build
```

---

## ✅ Recommended Path Forward

**Option 1: GitHub Actions (Best)**
1. Commit and push the fixed code
2. GitHub Action triggers automatically
3. Azure builds with cloud resources (16GB+ RAM)
4. Deployment completes in 5-10 minutes

**Option 2: Increase Local Memory**
1. Set `NODE_OPTIONS="--max-old-space-size=8192"`
2. Retry `pnpm build`
3. Deploy built artifacts with SWA CLI

**Option 3: Skip Local Build**
1. Deploy source code directly to Azure
2. Let Azure build in the cloud
3. Monitor deployment in Azure Portal

---

## 🔍 Verification After Deployment

```bash
# Check frontend URL
curl -I https://orange-river-0ce07e10f.6.azurestaticapps.net

# Test backend connectivity
# Open browser DevTools → Network tab
# Visit frontend URL
# Check API calls go to: https://carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io
```

---

## 📊 Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| Code Quality | ✅ Fixed | All ESLint errors resolved |
| Local Build | ❌ OOM | System resource limits |
| Azure Backend | ✅ Running | Deployed and operational |
| Frontend Deployment | ⏳ Pending | Need to use cloud build |

**Next Action:** Choose deployment method and proceed with cloud build.
