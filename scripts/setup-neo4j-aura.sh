#!/bin/bash
# Setup Neo4j Aura Free for CarbonScope BIM Graph
# Usage: ./scripts/setup-neo4j-aura.sh

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🟢 CarbonScope - Neo4j Aura Free Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "📝 Neo4j Aura Free Setup Guide"
echo ""
echo "Neo4j Aura Free cannot be created via CLI (no API for free tier)."
echo "Follow these steps to set up manually:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 1: Create Neo4j Aura Account"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. Visit: https://neo4j.com/cloud/aura-free/"
echo "2. Click 'Start Free'"
echo "3. Sign up with:"
echo "   • Email + Password"
echo "   • OR Google account"
echo "   • OR GitHub account"
echo ""
read -p "Press ENTER when you've created your account..." dummy

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 2: Create Free Instance"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1. In Aura Console, click 'New Instance'"
echo "2. Select 'AuraDB Free'"
echo "3. Instance settings:"
echo "   Name: carbonscope-bim"
echo "   Region: Choose closest to your users"
echo "4. Click 'Create'"
echo ""
echo "⚠️  IMPORTANT: Save the password shown on next screen!"
echo "   It will only be shown ONCE and cannot be recovered!"
echo ""
read -p "Press ENTER when instance is created..." dummy

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "STEP 3: Enter Connection Details"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Prompt for connection details
read -p "Enter Neo4j URI (e.g., neo4j+s://xxxxx.databases.neo4j.io): " NEO4J_URI
read -p "Enter Neo4j Username [default: neo4j]: " NEO4J_USER
NEO4J_USER=${NEO4J_USER:-neo4j}
read -sp "Enter Neo4j Password: " NEO4J_PASSWORD
echo ""

# Validate inputs
if [ -z "$NEO4J_URI" ] || [ -z "$NEO4J_PASSWORD" ]; then
    echo "❌ URI and password are required!"
    exit 1
fi

echo ""
echo "✅ Connection details saved"
echo ""

# Save credentials
CREDENTIALS_FILE="neo4j-aura-credentials.txt"
cat > "$CREDENTIALS_FILE" << EOF
# Neo4j Aura Credentials
# Created: $(date)

# Connection Details
NEO4J_URI="$NEO4J_URI"
NEO4J_USER="$NEO4J_USER"
NEO4J_PASSWORD="$NEO4J_PASSWORD"

# Aura Console
# https://console.neo4j.io/

# Browser Access
# Open in Neo4j Browser: $NEO4J_URI
# Username: $NEO4J_USER
# Password: (see above)

# Python Connection
from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "$NEO4J_URI",
    auth=("$NEO4J_USER", "$NEO4J_PASSWORD")
)

# Cypher Shell (CLI)
cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASSWORD"
EOF

echo "💾 Credentials saved to: $CREDENTIALS_FILE"
echo "   ⚠️  Keep this file secure and DO NOT commit to Git!"
echo ""

# Update .env
cat > backend/.env.neo4j << EOF
# Neo4j Aura Configuration
# Generated: $(date)

NEO4J_URI="$NEO4J_URI"
NEO4J_USER="$NEO4J_USER"
NEO4J_PASSWORD="$NEO4J_PASSWORD"
EOF

echo "💾 Environment config saved to: backend/.env.neo4j"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
if [ -f "pyproject.toml" ]; then
    if grep -q "neo4j" pyproject.toml; then
        echo "   neo4j driver already in dependencies"
    else
        echo "   Adding neo4j driver..."
        uv add neo4j
    fi
else
    echo "   ⚠️  pyproject.toml not found"
fi
cd ..

echo ""

# Test connection
echo "🧪 Testing connection..."
python3 << PYTHON
try:
    from neo4j import GraphDatabase
    driver = GraphDatabase.driver(
        "$NEO4J_URI",
        auth=("$NEO4J_USER", "$NEO4J_PASSWORD")
    )
    with driver.session() as session:
        result = session.run("RETURN 'Connection successful!' as message")
        print(f"✅ {result.single()['message']}")
    driver.close()
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("   Check your credentials and try again")
PYTHON

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Neo4j Aura Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "💰 Cost: FREE FOREVER"
echo ""
echo "📊 Free Tier Limits:"
echo "   • 200,000 nodes"
echo "   • 400,000 relationships"
echo "   • 1 GB RAM"
echo "   • 50 GB storage"
echo "   • No credit card required"
echo ""
echo "💡 Capacity for CarbonScope:"
echo "   • ~100 medium-sized buildings"
echo "   • Unlimited queries"
echo "   • Always-on (no auto-pause)"
echo ""
echo "Next steps:"
echo "1. Copy credentials from $CREDENTIALS_FILE to backend/.env"
echo "2. Open Neo4j Browser: $NEO4J_URI"
echo "3. Run sample queries to test"
echo "4. Migrate data from GraphDB (see GRAPH_DATABASE_MIGRATION.md)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📚 Sample Cypher Queries for Testing"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
cat << 'CYPHER'
// Create a sample building
CREATE (b:Building {
  id: 'building-001',
  name: 'Sample Office Building',
  location: 'San Francisco, CA',
  created_at: datetime()
})
RETURN b

// Create materials
CREATE (m1:Material {id: 'concrete-001', name: 'Concrete C30/37', carbon_factor: 150})
CREATE (m2:Material {id: 'steel-001', name: 'Structural Steel', carbon_factor: 2500})
RETURN m1, m2

// Create lifecycle stages (EN 15978)
CREATE (s1:LifecycleStage {code: 'A1-A3', name: 'Product Stage'})
CREATE (s2:LifecycleStage {code: 'A4', name: 'Transport'})
CREATE (s3:LifecycleStage {code: 'B6', name: 'Operational Energy'})
CREATE (s4:LifecycleStage {code: 'C1-C4', name: 'End of Life'})
RETURN s1, s2, s3, s4

// Link materials to lifecycle stages
MATCH (m:Material {id: 'concrete-001'})
MATCH (s:LifecycleStage {code: 'A1-A3'})
CREATE (m)-[:IN_STAGE]->(s)

// Create building elements
MATCH (b:Building {id: 'building-001'})
CREATE (b)-[:CONTAINS]->(floor:Floor {id: 'floor-1', name: 'Ground Floor'})
CREATE (floor)-[:CONTAINS]->(column:Element {id: 'column-1', name: 'Column C1', volume: 2.5})
RETURN column

// Add material to element
MATCH (e:Element {id: 'column-1'})
MATCH (m:Material {id: 'concrete-001'})
CREATE (e)-[r:MADE_OF {quantity: 2.5, carbon_kg: 375}]->(m)
RETURN r

// Query: Get total carbon for building
MATCH (b:Building {id: 'building-001'})-[:CONTAINS*]->(e:Element)
MATCH (e)-[r:MADE_OF]->(m:Material)
RETURN b.name, sum(r.carbon_kg) as total_carbon_kg

// Query: Carbon breakdown by lifecycle stage
MATCH (b:Building {id: 'building-001'})-[:CONTAINS*]->(e:Element)
MATCH (e)-[r:MADE_OF]->(m:Material)-[:IN_STAGE]->(s:LifecycleStage)
RETURN s.code, s.name, sum(r.carbon_kg) as carbon_kg
ORDER BY s.code
CYPHER

echo ""
echo "Copy these queries and run them in Neo4j Browser!"
echo ""
echo "Manage instance:"
echo "  • Aura Console: https://console.neo4j.io/"
echo "  • Browser: Click 'Open' in console"
echo "  • Pause instance: Not needed (free tier always on)"
echo ""
echo "Useful Cypher commands:"
echo "  MATCH (n) RETURN count(n)           # Count all nodes"
echo "  MATCH ()-[r]->() RETURN count(r)   # Count relationships"
echo "  CALL db.schema.visualization()     # View schema"
echo "  MATCH (n) DETACH DELETE n          # Clear all data (careful!)"
echo ""
