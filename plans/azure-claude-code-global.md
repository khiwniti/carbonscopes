cl# Global setup: Claude Code VS Code with Azure AI Foundry (Anthropic Claude Sonnet)

Important clarification
- Claude models are not available via Azure OpenAI. Use Azure AI Foundry remote Anthropic endpoint instead.
- The latest Sonnet on Azure AI often appears as IDs like claude-3-7-sonnet-YYYYMMDD. Use the newest Sonnet visible in your tenant.

Outcome
- Configure the Claude Code VS Code extension globally to call Azure AI Foundry's Anthropic remote endpoint using a Project API key.

---

## 0) Ready-to-run Azure CLI script (uses your current default subscription; region eastus2)
This script registers providers, ensures the Azure ML CLI extension is installed, creates a Resource Group and Azure AI Studio Workspace (ML workspace) in eastus2, then prints a deep link to open in Azure AI Studio to create a Project and Project API key.

```bash
#!/usr/bin/env bash
set -euo pipefail

LOCATION="eastus2"
RESOURCE_GROUP="ai-foundry-rg"
WORKSPACE="ai-foundry-ws"

SUBSCRIPTION_NAME=$(az account show --query name -o tsv)
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

echo "Using subscription: ${SUBSCRIPTION_NAME} (${SUBSCRIPTION_ID})"

echo "Registering resource providers..."
az provider register --namespace Microsoft.MachineLearningServices --wait
az provider register --namespace Microsoft.CognitiveServices --wait

echo "Ensuring Azure ML CLI extension is present..."
if ! az extension show --name ml >/dev/null 2>&1; then
  az extension add --name ml -y
else
  az extension update --name ml -y || true
fi

echo "Creating resource group ${RESOURCE_GROUP} in ${LOCATION} (idempotent)..."
az group create -n "${RESOURCE_GROUP}" -l "${LOCATION}" >/dev/null

echo "Creating or updating Azure AI Studio workspace ${WORKSPACE}..."
az ml workspace create -g "${RESOURCE_GROUP}" -w "${WORKSPACE}" -l "${LOCATION}"

WS_ID="/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.MachineLearningServices/workspaces/${WORKSPACE}"

echo
az ml workspace show -g "${RESOURCE_GROUP}" -w "${WORKSPACE}" -o table

echo
echo "Open Azure AI Studio to create a Project and Project API key:"
echo "  https://ai.azure.com/?wsid=${WS_ID}"
echo
echo "Next steps:"
echo "1) In Azure AI Studio, open the Workspace above and create a Project."
echo "2) In Project > Settings > Keys, create a Project API key and copy it."
```

---

## 1) cURL smoke test against Azure AI Anthropic remote endpoint
After you have a Project API key, verify access to Sonnet via the remote Anthropic endpoint.

```bash
# Replace with your Project API key and a Sonnet model enabled for your tenant
AZURE_AI_PROJECT_KEY="<PROJECT_API_KEY>"
MODEL_ID="claude-3-7-sonnet-20250219"  # or the latest available Sonnet

curl -sS https://models.inference.ai.azure.com/remote/anthropic/v1/messages \
  -H "Content-Type: application/json" \
  -H "api-key: $AZURE_AI_PROJECT_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -d '{
    "model": "'"$MODEL_ID"'",
    "max_tokens": 64,
    "messages": [ { "role": "user", "content": "Say hello" } ]
  }'
```

Expected: a valid JSON response with an assistant message.

---

## 2) Configure Claude Code VS Code extension (global)
Option A: Settings UI
- VS Code → Settings → Extensions → Claude Code
- Enable "Custom Server"
- Base URL: https://models.inference.ai.azure.com/remote/anthropic/v1
- API Key: paste your Azure AI Studio Project API key
- Model: your Sonnet model id (e.g., claude-3-7-sonnet-20250219)
- Reload VS Code

Option B: User settings JSON (avoid syncing secrets)
```json
{
  "claudeCode.experimental.customServer.enabled": true,
  "claudeCode.experimental.customServer.baseUrl": "https://models.inference.ai.azure.com/remote/anthropic/v1",
  "claudeCode.experimental.customServer.apiKey": "<PROJECT_API_KEY>",
  "claudeCode.model": "claude-3-7-sonnet-20250219"
}
```

Option C: Environment variables (only if your extension version honors them)
```bash
export ANTHROPIC_BASE_URL="https://models.inference.ai.azure.com/remote/anthropic/v1"
export ANTHROPIC_API_KEY="<PROJECT_API_KEY>"
export ANTHROPIC_VERSION="2023-06-01"
```
Restart VS Code and confirm the extension uses these.

---

## 3) Troubleshooting
- 401 Unauthorized: Verify you used a Project API key (Azure AI Studio), not Azure OpenAI, and the key is active.
- 404 Not Found: Ensure the base URL includes /remote/anthropic/v1 and you are posting to /messages.
- 400 Bad Request: Add required header anthropic-version: 2023-06-01.
- Model not found: Confirm the Sonnet model id is enabled in your region/tenant (test in Azure AI Studio Playground).
- Header mismatch: If the extension sends x-api-key and you cannot change it, use a tiny local proxy to map x-api-key → api-key and add anthropic-version.

---

## 4) VS Code verification
Open the Claude panel and ask a simple question. A successful response confirms your global wiring through Azure AI Foundry.
