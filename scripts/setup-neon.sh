#!/bin/bash
# Setup Neon (Serverless PostgreSQL) for CarbonScope
# Usage: ./scripts/setup-neon.sh

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 CarbonScope - Neon Database Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if neonctl is installed
if ! command -v neonctl &> /dev/null; then
    echo "📦 Installing Neon CLI..."
    npm install -g neonctl
fi

echo "🔐 Authenticating with Neon..."
echo "   Opening browser for authentication..."
neonctl auth

echo ""
echo "📁 Creating project..."
PROJECT_NAME="${1:-carbonscope}"
neonctl projects create --name "$PROJECT_NAME"

echo ""
echo "🌿 Creating branches..."
neonctl branches create --name dev
neonctl branches create --name staging

echo ""
echo "🔗 Getting connection strings..."
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 MAIN BRANCH (Production):"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
MAIN_URL=$(neonctl connection-string main --pooled)
echo "DATABASE_URL=\"$MAIN_URL\""
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 DEV BRANCH:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
DEV_URL=$(neonctl connection-string dev --pooled)
echo "DATABASE_URL=\"$DEV_URL\""
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 STAGING BRANCH:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
STAGING_URL=$(neonctl connection-string staging --pooled)
echo "DATABASE_URL=\"$STAGING_URL\""
echo ""

# Save to .env files
echo "💾 Saving to environment files..."

# Backend .env
cat > backend/.env.neon << EOF
# Neon Database Configuration
# Generated: $(date)

# Production (main branch)
DATABASE_URL="$MAIN_URL"

# Development
# DATABASE_URL="$DEV_URL"

# Staging
# DATABASE_URL="$STAGING_URL"
EOF

echo "✅ Saved to backend/.env.neon"
echo ""

# Offer to run migrations
read -p "🔄 Run database migrations now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🏃 Running migrations..."
    cd backend
    
    # Try different migration tools
    if [ -f "prisma/schema.prisma" ]; then
        echo "   Using Prisma..."
        npx prisma migrate deploy
    elif [ -d "../supabase/migrations" ]; then
        echo "   Using Supabase migrations..."
        psql "$MAIN_URL" < ../supabase/migrations/*.sql
    else
        echo "   ⚠️  No migrations found"
    fi
    
    cd ..
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Neon Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "1. Copy DATABASE_URL to backend/.env"
echo "2. Test connection: psql \$DATABASE_URL -c 'SELECT version();'"
echo "3. View in dashboard: https://console.neon.tech"
echo ""
echo "Branches:"
echo "  • main (prod)    - Production database"
echo "  • dev            - Development database"
echo "  • staging        - Staging database"
echo ""
echo "Switch branches:"
echo "  neonctl branches list"
echo "  neonctl connection-string <branch-name> --pooled"
echo ""
