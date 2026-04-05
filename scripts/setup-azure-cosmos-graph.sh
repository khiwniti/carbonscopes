#!/bin/bash
# Setup Azure Cosmos DB with Gremlin API for CarbonScope BIM Graph
# Usage: ./scripts/setup-azure-cosmos-graph.sh

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔷 CarbonScope - Azure Cosmos DB Graph Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Configuration
RESOURCE_GROUP="carbonscope-rg"
ACCOUNT_NAME="carbonscope-graph-$(date +%s)"
DATABASE_NAME="bim_carbon"
GRAPH_NAME="carbon_network"
LOCATION="${1:-eastus}"

echo "📋 Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Account: $ACCOUNT_NAME"
echo "   Database: $DATABASE_NAME"
echo "   Graph: $GRAPH_NAME"
echo "   Location: $LOCATION"
echo ""

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not installed"
    exit 1
fi

# Login check
echo "🔐 Checking Azure login..."
if ! az account show &> /dev/null; then
    az login
fi

SUBSCRIPTION=$(az account show --query "name" -o tsv)
echo "✅ Logged in to: $SUBSCRIPTION"
echo ""

# Create or check resource group
echo "📁 Checking resource group..."
if az group show --name "$RESOURCE_GROUP" &> /dev/null; then
    echo "   Resource group exists"
else
    echo "   Creating resource group..."
    az group create \
      --name "$RESOURCE_GROUP" \
      --location "$LOCATION" \
      --output table
fi
echo ""

# Create Cosmos DB account with Gremlin API
echo "🗄️  Creating Cosmos DB account with Gremlin API..."
echo "   ⏱️  This takes 5-10 minutes..."
echo ""

az cosmosdb create \
  --name "$ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --capabilities EnableGremlin \
  --default-consistency-level Session \
  --locations regionName="$LOCATION" failoverPriority=0 isZoneRedundant=False \
  --enable-free-tier true \
  --output table

echo ""
echo "✅ Cosmos DB account created!"
echo ""

# Create database
echo "📊 Creating Gremlin database..."
az cosmosdb gremlin database create \
  --account-name "$ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --name "$DATABASE_NAME" \
  --throughput 400 \
  --output table

echo ""

# Create graph with partition key
echo "🕸️  Creating graph (partitioned by buildingId)..."
az cosmosdb gremlin graph create \
  --account-name "$ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --database-name "$DATABASE_NAME" \
  --name "$GRAPH_NAME" \
  --partition-key-path "/buildingId" \
  --throughput 400 \
  --output table

echo ""

# Get connection details
echo "🔗 Getting connection details..."

ENDPOINT=$(az cosmosdb show \
  --name "$ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "writeLocations[0].documentEndpoint" \
  --output tsv)

# Convert HTTPS endpoint to WSS for Gremlin
GREMLIN_ENDPOINT=$(echo "$ENDPOINT" | sed 's/https:\/\//wss:\/\/' | sed 's/\.documents\./.gremlin./' | sed 's/$/443\//')

PRIMARY_KEY=$(az cosmosdb keys list \
  --name "$ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "primaryMasterKey" \
  --output tsv)

SECONDARY_KEY=$(az cosmosdb keys list \
  --name "$ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "secondaryMasterKey" \
  --output tsv)

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 CONNECTION DETAILS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Gremlin Endpoint: $GREMLIN_ENDPOINT"
echo "Database: $DATABASE_NAME"
echo "Graph: $GRAPH_NAME"
echo ""
echo "Primary Key: $PRIMARY_KEY"
echo "Secondary Key: $SECONDARY_KEY"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save credentials
CREDENTIALS_FILE="azure-cosmos-credentials.txt"
cat > "$CREDENTIALS_FILE" << EOF
# Azure Cosmos DB Gremlin Credentials
# Created: $(date)
# Resource Group: $RESOURCE_GROUP
# Account: $ACCOUNT_NAME

# Connection Details
COSMOS_GREMLIN_ENDPOINT="$GREMLIN_ENDPOINT"
COSMOS_GREMLIN_KEY="$PRIMARY_KEY"
COSMOS_DATABASE="$DATABASE_NAME"
COSMOS_GRAPH="$GRAPH_NAME"

# Azure Portal
# https://portal.azure.com/#@/resource/subscriptions/$(az account show --query "id" -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.DocumentDB/databaseAccounts/$ACCOUNT_NAME

# Python Connection
from gremlin_python.driver import client, serializer

gremlin_client = client.Client(
    url="$GREMLIN_ENDPOINT",
    traversal_source="g",
    username="/dbs/$DATABASE_NAME/colls/$GRAPH_NAME",
    password="$PRIMARY_KEY",
    message_serializer=serializer.GraphSONSerializersV2d0()
)
EOF

echo "💾 Credentials saved to: $CREDENTIALS_FILE"
echo "   ⚠️  Keep this file secure and DO NOT commit to Git!"
echo ""

# Update .env
cat > backend/.env.cosmos << EOF
# Azure Cosmos DB Gremlin Configuration
# Generated: $(date)

COSMOS_GREMLIN_ENDPOINT="$GREMLIN_ENDPOINT"
COSMOS_GREMLIN_KEY="$PRIMARY_KEY"
COSMOS_DATABASE="$DATABASE_NAME"
COSMOS_GRAPH="$GRAPH_NAME"
EOF

echo "💾 Environment config saved to: backend/.env.cosmos"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
if [ -f "pyproject.toml" ]; then
    if grep -q "gremlinpython" pyproject.toml; then
        echo "   gremlinpython already in dependencies"
    else
        echo "   Adding gremlinpython..."
        uv add gremlinpython
    fi
else
    echo "   ⚠️  pyproject.toml not found"
fi
cd ..

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Azure Cosmos DB Graph Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💰 Cost: FREE TIER (1000 RU/s + 25GB forever)"
echo "   You're using 400 RU/s (graph + database)"
echo "   600 RU/s still available for other containers"
echo ""
echo "📊 Free Tier Limits:"
echo "   • 1000 Request Units/second"
echo "   • 25 GB storage"
echo "   • Unlimited number of containers"
echo ""
echo "Next steps:"
echo "1. Copy credentials from $CREDENTIALS_FILE to backend/.env"
echo "2. Install gremlinpython: cd backend && uv add gremlinpython"
echo "3. Test connection with sample query"
echo "4. Migrate data from GraphDB (see GRAPH_DATABASE_MIGRATION.md)"
echo ""
echo "Manage Cosmos DB:"
echo "  • Portal: https://portal.azure.com"
echo "  • Data Explorer: Test queries in browser"
echo "  • Metrics: Monitor RU/s usage"
echo ""
echo "Useful commands:"
echo "  az cosmosdb show -g $RESOURCE_GROUP -n $ACCOUNT_NAME"
echo "  az cosmosdb gremlin graph show -g $RESOURCE_GROUP -a $ACCOUNT_NAME -d $DATABASE_NAME -n $GRAPH_NAME"
echo ""
echo "Delete resources (when done):"
echo "  az cosmosdb delete -g $RESOURCE_GROUP -n $ACCOUNT_NAME --yes"
echo ""
