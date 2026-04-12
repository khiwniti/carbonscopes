# Azure Container Registry (ACR) Deployment Guide

Complete guide for deploying the carbonscope-init frontend to Azure Container Registry and Azure Container Apps.

## 📋 Prerequisites

### Required Tools
- **Azure CLI** (`az`) - [Install](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **Docker** - [Install](https://docs.docker.com/get-docker/)
- **Azure Subscription** with contributor access

### Required Services (Auto-created by script)
- Azure Container Registry (Basic SKU ~$5/month)
- Azure Container Apps Environment (~$15/month)
- Azure Container App (~$0-50/month based on usage)

**Estimated Monthly Cost:** $20-70/month

---

## 🚀 Quick Start

### 1. Login to Azure
```bash
az login
```

### 2. Deploy Everything
```bash
cd /teamspace/studios/this_studio/comprehensive-carbonscope-bim-agent/carbonscope-init
./deploy-frontend-acr.sh
```

This single command will:
1. ✅ Create Azure Container Registry
2. ✅ Build Docker image from `apps/frontend/Dockerfile.production`
3. ✅ Push image to ACR
4. ✅ Create Container Apps environment
5. ✅ Deploy frontend to Container Apps
6. ✅ Provide live URL

**Deployment Time:** ~15-20 minutes

---

## 🎯 Advanced Usage

### Build Only (No Deploy)
```bash
./deploy-frontend-acr.sh --build-only
```

### Push Existing Image
```bash
./deploy-frontend-acr.sh --push-only
```

### Deploy Only (Image already in ACR)
```bash
./deploy-frontend-acr.sh --deploy-only
```

### Custom Image Tag
```bash
IMAGE_TAG=v1.2.3 ./deploy-frontend-acr.sh
```

---

## 🔧 Configuration

### Environment Variables

The script uses these default values:

```bash
# Project Configuration
PROJECT_NAME="carbonscope"
RESOURCE_GROUP="carbonscope-rg"
LOCATION="eastus"

# Container Registry
ACR_NAME="carbonscopeacr"

# Container App
FRONTEND_APP="carbonscope-frontend"

# Docker Image
IMAGE_NAME="frontend"
IMAGE_TAG="latest"  # Override with: IMAGE_TAG=v2 ./deploy-frontend-acr.sh
```

### Runtime Environment Variables (Container App)

These are injected into the running container:

```bash
NODE_ENV=production
NEXT_TELEMETRY_DISABLED=1
NEXT_PUBLIC_BACKEND_URL=https://carbonscope-backend.wittybay-b8ab90d4.eastus.azurecontainerapps.io
```

To add more environment variables:

```bash
az containerapp update \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --set-env-vars \
    "NEXT_PUBLIC_API_KEY=your-key" \
    "CUSTOM_VAR=value"
```

---

## 📦 Docker Image Details

### Dockerfile
Location: `apps/frontend/Dockerfile.production`

### Multi-Stage Build
1. **Base**: Node.js 20 Alpine
2. **Dependencies**: Install pnpm + workspace deps
3. **Builder**: Build Next.js with 8GB memory
4. **Runner**: Production runtime (non-root user)

### Image Optimization
- ✅ Multi-stage build (smaller final image)
- ✅ Alpine Linux base (minimal footprint)
- ✅ Non-root user (security)
- ✅ Health check endpoint
- ✅ Monorepo-aware (handles workspace dependencies)

### Expected Image Size
~500MB-1GB (varies based on dependencies)

---

## 🔍 Monitoring & Debugging

### View Live Logs
```bash
az containerapp logs show \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --follow
```

### Check Container Status
```bash
az containerapp show \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --query "{Status:properties.provisioningState, URL:properties.configuration.ingress.fqdn}"
```

### View ACR Images
```bash
az acr repository list --name carbonscopeacr --output table
```

### View Image Tags
```bash
az acr repository show-tags \
  --name carbonscopeacr \
  --repository frontend \
  --output table
```

### Restart Container
```bash
az containerapp revision restart \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --revision $(az containerapp revision list \
    --name carbonscope-frontend \
    --resource-group carbonscope-rg \
    --query "[0].name" -o tsv)
```

---

## 📈 Scaling

### Manual Scaling
```bash
az containerapp update \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --min-replicas 2 \
  --max-replicas 10
```

### Auto-scaling Rules
```bash
az containerapp update \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --scale-rule-name http-scaling \
  --scale-rule-type http \
  --scale-rule-http-concurrency 100
```

---

## 🔄 CI/CD with GitHub Actions

### Setup

1. **Create Service Principal:**
```bash
az ad sp create-for-rbac \
  --name "carbonscope-github-actions" \
  --role contributor \
  --scopes /subscriptions/$(az account show --query id -o tsv)/resourceGroups/carbonscope-rg \
  --sdk-auth
```

2. **Add GitHub Secrets:**
   - `AZURE_CREDENTIALS` - Output from above command
   - `ACR_NAME` - `carbonscopeacr`
   - `ACR_USERNAME` - Get from: `az acr credential show --name carbonscopeacr --query username -o tsv`
   - `ACR_PASSWORD` - Get from: `az acr credential show --name carbonscopeacr --query passwords[0].value -o tsv`

3. **Workflow File:**
See `.github/workflows/deploy-frontend-acr.yml`

---

## 🔐 Security Best Practices

### 1. Use Managed Identity (Recommended)
```bash
# Enable system-assigned managed identity
az containerapp identity assign \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --system-assigned

# Configure ACR to allow managed identity
IDENTITY_ID=$(az containerapp identity show \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --query principalId -o tsv)

az role assignment create \
  --assignee $IDENTITY_ID \
  --role AcrPull \
  --scope $(az acr show --name carbonscopeacr --query id -o tsv)
```

### 2. Disable Admin User
```bash
az acr update --name carbonscopeacr --admin-enabled false
```

### 3. Use Azure Key Vault for Secrets
```bash
# Create Key Vault
az keyvault create \
  --name carbonscope-kv \
  --resource-group carbonscope-rg \
  --location eastus

# Store secrets
az keyvault secret set \
  --vault-name carbonscope-kv \
  --name "database-url" \
  --value "postgresql://..."

# Reference in Container App
az containerapp update \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --set-env-vars \
    "DATABASE_URL=secretref:database-url"
```

---

## 🆘 Troubleshooting

### Build Fails with Out of Memory
**Solution:** Increase Docker memory or use GitHub Actions (16GB RAM available)

### Image Push Fails
**Solutions:**
1. Check ACR login: `az acr login --name carbonscopeacr`
2. Verify credentials: `az acr credential show --name carbonscopeacr`
3. Check network connectivity to ACR

### Container App Won't Start
**Debugging Steps:**
1. Check logs: `az containerapp logs show --name carbonscope-frontend --resource-group carbonscope-rg --follow`
2. Verify image exists in ACR: `az acr repository show --name carbonscopeacr --image frontend:latest`
3. Check environment variables: `az containerapp show --name carbonscope-frontend --resource-group carbonscope-rg --query properties.configuration.secrets`

### Health Check Failing
**Common Causes:**
- Wrong port (should be 3000)
- Next.js not starting properly
- Missing environment variables
- Database connection issues

**Check:** `curl https://your-app-url.azurecontainerapps.io/`

---

## 🗑️ Cleanup

### Delete Everything
```bash
az group delete --name carbonscope-rg --yes --no-wait
```

### Delete Only Container App
```bash
az containerapp delete \
  --name carbonscope-frontend \
  --resource-group carbonscope-rg \
  --yes
```

### Delete Only ACR
```bash
az acr delete \
  --name carbonscopeacr \
  --resource-group carbonscope-rg \
  --yes
```

---

## 📊 Cost Optimization

### Free Tier Options
- ❌ ACR - No free tier (Basic starts at $5/month)
- ✅ Container Apps - Free allowance: 180,000 vCPU-seconds/month
- ✅ Azure Monitor - First 5GB free/month

### Cost Reduction Tips
1. **Use Container Apps Consumption Plan** (pay per second)
2. **Scale to zero** when not in use
3. **Use cheaper regions** (like East US vs West Europe)
4. **Delete unused images** from ACR
5. **Use spot instances** for non-prod environments

### Monitor Costs
```bash
az consumption usage list \
  --start-date $(date -d "30 days ago" +%Y-%m-%d) \
  --end-date $(date +%Y-%m-%d) \
  --query "[?contains(instanceName, 'carbonscope')].{Service:meterName, Cost:pretaxCost}" \
  --output table
```

---

## 🔗 Useful Links

- [Azure Container Registry Docs](https://learn.microsoft.com/en-us/azure/container-registry/)
- [Azure Container Apps Docs](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Next.js Docker Docs](https://nextjs.org/docs/deployment#docker-image)
- [Azure CLI Reference](https://learn.microsoft.com/en-us/cli/azure/)

---

## 📞 Support

**Issues?** Check:
1. Build logs: `/tmp/docker-build.log`
2. Container logs: `az containerapp logs show --follow`
3. Azure Portal: https://portal.azure.com

**Questions?** Contact BKS DevOps team
