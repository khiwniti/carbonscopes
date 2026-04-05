#!/bin/bash
# Setup Azure PostgreSQL Flexible Server (Free Tier) for CarbonScope
# Usage: ./scripts/setup-azure-postgres.sh

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔷 CarbonScope - Azure PostgreSQL Setup (Free Tier)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Configuration
RESOURCE_GROUP="carbonscope-rg"
SERVER_NAME="carbonscope-db-$(date +%s)"  # Unique name with timestamp
LOCATION="${1:-eastus}"  # Default to East US
ADMIN_USER="carbonadmin"
DB_NAME="carbonscope_prod"

echo "📋 Configuration:"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Server Name: $SERVER_NAME"
echo "   Location: $LOCATION"
echo "   Admin User: $ADMIN_USER"
echo "   Database: $DB_NAME"
echo ""

# Check Azure CLI
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI not installed"
    echo "   Install: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

# Login check
echo "🔐 Checking Azure login..."
if ! az account show &> /dev/null; then
    echo "   Please login to Azure..."
    az login
fi

# Show current subscription
SUBSCRIPTION=$(az account show --query "name" -o tsv)
echo "✅ Logged in to subscription: $SUBSCRIPTION"
echo ""

# Generate secure password
echo "🔑 Generating secure password..."
ADMIN_PASSWORD=$(openssl rand -base64 24 | tr -d "=+/" | cut -c1-20)Aa1!
echo "   Password generated (save this!): $ADMIN_PASSWORD"
echo ""

# Create resource group
echo "📁 Creating resource group..."
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output table

echo ""

# Create PostgreSQL Flexible Server (Free Tier)
echo "🗄️  Creating PostgreSQL Flexible Server..."
echo "   ⏱️  This takes 5-10 minutes..."
echo ""

az postgres flexible-server create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --location "$LOCATION" \
  --admin-user "$ADMIN_USER" \
  --admin-password "$ADMIN_PASSWORD" \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 16 \
  --public-access 0.0.0.0 \
  --yes

echo ""
echo "✅ Server created!"
echo ""

# Configure firewall
echo "🔥 Configuring firewall rules..."

# Get current IP
MY_IP=$(curl -s ifconfig.me)
echo "   Your IP: $MY_IP"

az postgres flexible-server firewall-rule create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --rule-name AllowMyIP \
  --start-ip-address "$MY_IP" \
  --end-ip-address "$MY_IP" \
  --output table

# Allow Azure services
az postgres flexible-server firewall-rule create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0 \
  --output table

echo ""

# Create database
echo "📊 Creating database: $DB_NAME..."
az postgres flexible-server db create \
  --resource-group "$RESOURCE_GROUP" \
  --server-name "$SERVER_NAME" \
  --database-name "$DB_NAME" \
  --output table

echo ""

# Get connection details
echo "🔗 Getting connection details..."
FQDN=$(az postgres flexible-server show \
  --resource-group "$RESOURCE_GROUP" \
  --name "$SERVER_NAME" \
  --query "fullyQualifiedDomainName" \
  --output tsv)

# Build connection string
CONNECTION_STRING="postgresql://${ADMIN_USER}:${ADMIN_PASSWORD}@${FQDN}:5432/${DB_NAME}?sslmode=require"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 CONNECTION DETAILS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Server: $FQDN"
echo "Database: $DB_NAME"
echo "Username: $ADMIN_USER"
echo "Password: $ADMIN_PASSWORD"
echo ""
echo "Connection String:"
echo "$CONNECTION_STRING"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Save credentials
CREDENTIALS_FILE="azure-postgres-credentials.txt"
cat > "$CREDENTIALS_FILE" << EOF
# Azure PostgreSQL Credentials
# Created: $(date)
# Resource Group: $RESOURCE_GROUP
# Server: $SERVER_NAME
# Location: $LOCATION

# Connection Details
DATABASE_URL="$CONNECTION_STRING"

# Azure Portal
# https://portal.azure.com/#@/resource/subscriptions/$(az account show --query "id" -o tsv)/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.DBforPostgreSQL/flexibleServers/$SERVER_NAME

# Credentials (SAVE THESE SECURELY!)
Host: $FQDN
Port: 5432
Database: $DB_NAME
Username: $ADMIN_USER
Password: $ADMIN_PASSWORD

# psql Connection
psql "postgresql://${ADMIN_USER}:${ADMIN_PASSWORD}@${FQDN}:5432/${DB_NAME}?sslmode=require"
EOF

echo "💾 Credentials saved to: $CREDENTIALS_FILE"
echo "   ⚠️  Keep this file secure and DO NOT commit to Git!"
echo ""

# Update .env
cat > backend/.env.azure << EOF
# Azure PostgreSQL Configuration
# Generated: $(date)

DATABASE_URL="$CONNECTION_STRING"
EOF

echo "💾 Environment config saved to: backend/.env.azure"
echo ""

# Test connection
echo "🧪 Testing connection..."
if command -v psql &> /dev/null; then
    psql "$CONNECTION_STRING" -c "SELECT version();" && echo "✅ Connection successful!"
else
    echo "⚠️  psql not installed. Install PostgreSQL client to test connection."
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Azure PostgreSQL Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💰 Cost: FREE for 12 months (Azure Free Tier)"
echo "   After 12 months: ~$12.41/month"
echo ""
echo "Next steps:"
echo "1. Copy DATABASE_URL from $CREDENTIALS_FILE to backend/.env"
echo "2. Run migrations: cd backend && npx prisma migrate deploy"
echo "3. View in Azure Portal: https://portal.azure.com"
echo ""
echo "Manage server:"
echo "  az postgres flexible-server show -g $RESOURCE_GROUP -n $SERVER_NAME"
echo "  az postgres flexible-server restart -g $RESOURCE_GROUP -n $SERVER_NAME"
echo "  az postgres flexible-server stop -g $RESOURCE_GROUP -n $SERVER_NAME"
echo "  az postgres flexible-server start -g $RESOURCE_GROUP -n $SERVER_NAME"
echo ""
echo "Delete resources (when done):"
echo "  az group delete --name $RESOURCE_GROUP --yes"
echo ""
