# Graph Database Cloud Migration Guide

## Current Setup
- **Local:** Ontotext GraphDB 10.7.0 (RDF/SPARQL)
- **Port:** 7200
- **Use Case:** BIM relationships, carbon tracking, EN 15978 lifecycle stages

---

## 🎯 Cloud Graph Database Options (Free Tier)

| Provider | Type | Query Language | Free Tier | Best For |
|----------|------|----------------|-----------|----------|
| **Azure Cosmos DB** | Property Graph | Gremlin/Cypher | 1000 RU/s + 25GB | Azure ecosystem, global distribution |
| **Neo4j Aura Free** | Property Graph | Cypher | 200k nodes, 400k relationships | Complex BIM hierarchies |
| **Amazon Neptune** | Both | Gremlin/SPARQL | No free tier | RDF + Property graph |
| **ArangoDB Oasis** | Multi-model | AQL | 8GB RAM, 50GB storage | Document + Graph hybrid |
| **Memgraph Cloud** | Property Graph | Cypher | 1GB RAM, 10GB storage | Real-time analytics |
| **Ontotext GraphDB Cloud** | RDF/Semantic | SPARQL | Free trial (30 days) | Zero migration (same DB) |

---

## 🔷 Option 1: Azure Cosmos DB with Gremlin API (Recommended for Azure)

### Why Cosmos DB for BIM/Carbon Tracking?
- ✅ **Multi-model**: Graph + Document database
- ✅ **Global distribution**: Low latency worldwide
- ✅ **Elastic scale**: Auto-scales with demand
- ✅ **SLA**: 99.999% availability
- ✅ **Free tier**: 1000 RU/s forever (enough for dev/small prod)
- ✅ **Integration**: Works with Azure Functions, App Services

### Architecture for CarbonScope

```
PostgreSQL (Neon)           → User data, auth, projects
     ↓
Cosmos DB (Gremlin)         → BIM relationships, carbon flows
     ↓
├─ Buildings (vertices)     → IFC entities
├─ Materials (vertices)     → Material library
├─ Lifecycle Stages (vertices) → EN 15978 stages (A1-A3, B6, C1-C4, D)
├─ CONTAINS (edges)         → Building → Spaces → Elements
├─ MADE_OF (edges)          → Element → Material
├─ EMITS (edges)            → Material → Carbon (with quantity)
└─ IN_STAGE (edges)         → Carbon → Lifecycle Stage
```

### Setup with Azure CLI

#### Step 1: Create Cosmos DB Account

```bash
#!/bin/bash
# Setup Azure Cosmos DB for CarbonScope

RESOURCE_GROUP="carbonscope-rg"
ACCOUNT_NAME="carbonscope-graph"
DATABASE_NAME="bim_carbon"
GRAPH_NAME="carbon_network"
LOCATION="eastus"

# Create Cosmos DB account with Gremlin API
az cosmosdb create \
  --name "$ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --capabilities EnableGremlin \
  --default-consistency-level Session \
  --locations regionName="$LOCATION" failoverPriority=0 isZoneRedundant=False \
  --enable-free-tier true

# Create database
az cosmosdb gremlin database create \
  --account-name "$ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --name "$DATABASE_NAME" \
  --throughput 400  # 400 RU/s (can use up to 1000 with free tier)

# Create graph
az cosmosdb gremlin graph create \
  --account-name "$ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --database-name "$DATABASE_NAME" \
  --name "$GRAPH_NAME" \
  --partition-key-path "/buildingId"
```

#### Step 2: Get Connection Details

```bash
# Get endpoint
ENDPOINT=$(az cosmosdb show \
  --name "$ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "writeLocations[0].documentEndpoint" \
  --output tsv)

# Get primary key
PRIMARY_KEY=$(az cosmosdb keys list \
  --name "$ACCOUNT_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --query "primaryMasterKey" \
  --output tsv)

echo "Gremlin Endpoint: $ENDPOINT"
echo "Primary Key: $PRIMARY_KEY"
```

#### Step 3: Python Client Setup

```python
# backend/core/graph/cosmos_client.py
from gremlin_python.driver import client, serializer
import os

class CosmosGraphClient:
    def __init__(self):
        self.endpoint = os.getenv("COSMOS_GREMLIN_ENDPOINT")
        self.key = os.getenv("COSMOS_GREMLIN_KEY")
        self.database = os.getenv("COSMOS_DATABASE", "bim_carbon")
        self.graph = os.getenv("COSMOS_GRAPH", "carbon_network")
        
        self.client = client.Client(
            url=f"{self.endpoint}",
            traversal_source="g",
            username=f"/dbs/{self.database}/colls/{self.graph}",
            password=self.key,
            message_serializer=serializer.GraphSONSerializersV2d0()
        )
    
    async def add_building(self, building_id: str, name: str, location: str):
        """Add a building vertex"""
        query = f"""
            g.addV('building')
             .property('id', '{building_id}')
             .property('name', '{name}')
             .property('location', '{location}')
             .property('buildingId', '{building_id}')
        """
        return await self.client.submit_async(query)
    
    async def add_material_to_element(
        self, 
        element_id: str, 
        material_id: str, 
        quantity: float,
        carbon_kg: float
    ):
        """Create MADE_OF edge with carbon emission"""
        query = f"""
            g.V('{element_id}')
             .addE('MADE_OF')
             .to(g.V('{material_id}'))
             .property('quantity', {quantity})
             .property('carbon_kg', {carbon_kg})
             .property('timestamp', '{datetime.utcnow().isoformat()}')
        """
        return await self.client.submit_async(query)
    
    async def get_building_carbon_footprint(self, building_id: str):
        """Calculate total carbon for a building"""
        query = f"""
            g.V().has('building', 'id', '{building_id}')
             .repeat(out('CONTAINS'))
             .emit()
             .outE('MADE_OF')
             .values('carbon_kg')
             .sum()
        """
        result = await self.client.submit_async(query)
        return result.all().result()[0]
    
    async def get_lifecycle_breakdown(self, building_id: str):
        """Get carbon by EN 15978 lifecycle stage"""
        query = f"""
            g.V().has('building', 'id', '{building_id}')
             .repeat(out('CONTAINS'))
             .emit()
             .outE('MADE_OF')
             .as('carbon')
             .inV()
             .out('IN_STAGE')
             .as('stage')
             .select('stage', 'carbon')
             .by('name')
             .by('carbon_kg')
             .group()
             .by(select('stage'))
             .by(select('carbon').sum())
        """
        result = await self.client.submit_async(query)
        return result.all().result()
```

#### Step 4: Environment Variables

```env
# backend/.env
COSMOS_GREMLIN_ENDPOINT="wss://carbonscope-graph.gremlin.cosmos.azure.com:443/"
COSMOS_GREMLIN_KEY="your-primary-key-here"
COSMOS_DATABASE="bim_carbon"
COSMOS_GRAPH="carbon_network"
```

---

## 🟢 Option 2: Neo4j Aura Free (Best for Property Graphs)

### Why Neo4j for BIM?
- ✅ **Free tier**: 200k nodes, 400k relationships (enough for medium buildings)
- ✅ **Cypher**: More intuitive than Gremlin for complex queries
- ✅ **APOC**: Advanced procedures library
- ✅ **Visualization**: Built-in graph browser
- ✅ **Performance**: Optimized for traversals

### Setup Steps

#### 1. Create Neo4j Aura Account
```bash
# Visit https://neo4j.com/cloud/aura-free/
# Sign up with email
# Create new instance (select Free tier)
# Save credentials immediately (shown only once!)
```

#### 2. Connection Details
```
URI: neo4j+s://xxxxx.databases.neo4j.io
Username: neo4j
Password: (generated password)
```

#### 3. Python Client

```python
# backend/core/graph/neo4j_client.py
from neo4j import GraphDatabase
import os

class Neo4jClient:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def add_building(self, building_id: str, name: str, location: str):
        """Add a building node"""
        with self.driver.session() as session:
            return session.run("""
                CREATE (b:Building {
                    id: $building_id,
                    name: $name,
                    location: $location,
                    created_at: datetime()
                })
                RETURN b
            """, building_id=building_id, name=name, location=location).single()
    
    def add_material_to_element(
        self, 
        element_id: str, 
        material_id: str, 
        quantity: float,
        carbon_kg: float
    ):
        """Create MADE_OF relationship"""
        with self.driver.session() as session:
            return session.run("""
                MATCH (e:Element {id: $element_id})
                MATCH (m:Material {id: $material_id})
                CREATE (e)-[r:MADE_OF {
                    quantity: $quantity,
                    carbon_kg: $carbon_kg,
                    timestamp: datetime()
                }]->(m)
                RETURN r
            """, 
                element_id=element_id,
                material_id=material_id,
                quantity=quantity,
                carbon_kg=carbon_kg
            ).single()
    
    def get_building_carbon_footprint(self, building_id: str):
        """Calculate total carbon for a building"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (b:Building {id: $building_id})-[:CONTAINS*]->(e:Element)
                MATCH (e)-[r:MADE_OF]->(m:Material)
                RETURN sum(r.carbon_kg) as total_carbon
            """, building_id=building_id).single()
            return result["total_carbon"] if result else 0
    
    def get_lifecycle_breakdown(self, building_id: str):
        """Get carbon by EN 15978 lifecycle stage"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (b:Building {id: $building_id})-[:CONTAINS*]->(e:Element)
                MATCH (e)-[r:MADE_OF]->(m:Material)-[:IN_STAGE]->(s:LifecycleStage)
                RETURN s.name as stage, sum(r.carbon_kg) as carbon
                ORDER BY carbon DESC
            """, building_id=building_id)
            return {record["stage"]: record["carbon"] for record in result}
```

#### 4. Environment Variables

```env
# backend/.env
NEO4J_URI="neo4j+s://xxxxx.databases.neo4j.io"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="your-generated-password"
```

---

## 🔄 Migration from Ontotext GraphDB

### Strategy: Convert RDF/SPARQL → Property Graph

#### Step 1: Export from GraphDB

```sparql
# Export all triples
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX carbon: <http://carbonscope.io/ontology#>

SELECT ?subject ?predicate ?object
WHERE {
    ?subject ?predicate ?object
}
```

Save as `graphdb_export.ttl` (Turtle format)

#### Step 2: Convert RDF to Property Graph

```python
# scripts/convert_rdf_to_graph.py
from rdflib import Graph
from neo4j import GraphDatabase

def convert_rdf_to_neo4j(ttl_file: str, neo4j_uri: str, neo4j_auth: tuple):
    """Convert RDF triples to Neo4j property graph"""
    
    # Load RDF
    g = Graph()
    g.parse(ttl_file, format="turtle")
    
    # Connect to Neo4j
    driver = GraphDatabase.driver(neo4j_uri, auth=neo4j_auth)
    
    with driver.session() as session:
        # Convert triples to nodes and relationships
        for subject, predicate, obj in g:
            # Create/merge subject node
            session.run("""
                MERGE (s:Resource {uri: $uri})
                SET s.label = $label
            """, uri=str(subject), label=subject.split("#")[-1])
            
            # Handle object-property vs datatype-property
            if isinstance(obj, URIRef):
                # Object property → relationship
                session.run("""
                    MATCH (s:Resource {uri: $subject})
                    MERGE (o:Resource {uri: $object})
                    MERGE (s)-[r:RELATES {type: $predicate}]->(o)
                """, 
                    subject=str(subject),
                    object=str(obj),
                    predicate=str(predicate)
                )
            else:
                # Datatype property → node property
                session.run("""
                    MATCH (s:Resource {uri: $subject})
                    SET s[$key] = $value
                """,
                    subject=str(subject),
                    key=predicate.split("#")[-1],
                    value=str(obj)
                )
    
    driver.close()
    print(f"✅ Converted {len(g)} triples to Neo4j")

# Usage
convert_rdf_to_neo4j(
    "graphdb_export.ttl",
    "neo4j+s://xxxxx.databases.neo4j.io",
    ("neo4j", "password")
)
```

---

## 📊 Comparison: RDF vs Property Graph for BIM

### When to Use RDF/SPARQL (Ontotext GraphDB)
✅ **Ontology-driven modeling** (IFC standards, buildingSMART)  
✅ **Semantic reasoning** (infer relationships)  
✅ **Standards compliance** (RDF/OWL required)  
✅ **Integration with other RDF data sources**  

### When to Use Property Graphs (Neo4j/Cosmos DB)
✅ **Performance** (faster traversals for BIM hierarchies)  
✅ **Developer experience** (Cypher more intuitive than SPARQL)  
✅ **Visualization** (better graph browsers)  
✅ **Cloud-native** (better managed services)  

### Hybrid Approach (Recommended for CarbonScope)

```
PostgreSQL (Neon)     → Structured data (users, projects, metadata)
       ↓
Neo4j Aura/Cosmos DB  → BIM relationships, carbon flows
       ↓
       ├─ Material library (nodes)
       ├─ Building elements (nodes)
       ├─ Carbon calculations (edges with properties)
       └─ Lifecycle stages (nodes)
```

**Why hybrid?**
- PostgreSQL: Better for CRUD, auth, transactional data
- Graph DB: Better for complex traversals (e.g., "find all materials in building X that contribute to lifecycle stage A1-A3")

---

## 🚀 Quick Start Scripts

### Azure Cosmos DB Setup

```bash
chmod +x scripts/setup-azure-cosmos-graph.sh
./scripts/setup-azure-cosmos-graph.sh
```

### Neo4j Aura Setup

```bash
chmod +x scripts/setup-neo4j-aura.sh
./scripts/setup-neo4j-aura.sh
```

---

## 💰 Cost Analysis (After Free Tier)

### Azure Cosmos DB
- **Free tier**: 1000 RU/s + 25GB forever
- **Paid**: ~$24/month (400 RU/s provisioned) or serverless (~$0.25/million requests)
- **Best for**: Variable workloads, global distribution

### Neo4j Aura
- **Free tier**: 200k nodes, 400k relationships forever
- **Professional**: $65/month (8GB memory, unlimited graph size)
- **Best for**: Fixed workloads, complex queries

### Recommendation for CarbonScope
- **Start**: Neo4j Aura Free (easier migration, better tooling)
- **Scale**: Azure Cosmos DB (when you need >400k relationships or global distribution)

---

## 📚 Example Queries

### Cypher (Neo4j)

```cypher
// Get total carbon for a building
MATCH (b:Building {id: 'building-123'})-[:CONTAINS*]->(e:Element)
MATCH (e)-[r:MADE_OF]->(m:Material)
RETURN sum(r.carbon_kg) as total_carbon_kg

// Find materials contributing most to carbon
MATCH (e:Element)-[r:MADE_OF]->(m:Material)
WHERE r.carbon_kg > 100
RETURN m.name, sum(r.carbon_kg) as total_carbon
ORDER BY total_carbon DESC
LIMIT 10

// Get carbon breakdown by lifecycle stage (EN 15978)
MATCH (b:Building {id: 'building-123'})-[:CONTAINS*]->(e:Element)
MATCH (e)-[r:MADE_OF]->(m:Material)-[:IN_STAGE]->(s:LifecycleStage)
RETURN s.code, s.name, sum(r.carbon_kg) as carbon_kg
ORDER BY s.code
```

### Gremlin (Azure Cosmos DB)

```gremlin
// Get total carbon for a building
g.V().has('building', 'id', 'building-123')
  .repeat(out('CONTAINS'))
  .emit()
  .outE('MADE_OF')
  .values('carbon_kg')
  .sum()

// Find materials contributing most to carbon
g.E().hasLabel('MADE_OF')
  .has('carbon_kg', gt(100))
  .project('material', 'carbon')
  .by(inV().values('name'))
  .by('carbon_kg')
  .group()
  .by(select('material'))
  .by(select('carbon').sum())
  .order(local).by(values, desc)
  .limit(local, 10)
```

---

## Next Steps

1. **Choose provider** (Neo4j Aura recommended for ease)
2. **Create account** (free, no credit card)
3. **Run setup script**
4. **Migrate sample data** (10-100 buildings)
5. **Test queries** (verify performance)
6. **Update application code** (switch from GraphDB client)
7. **Monitor usage** (stay within free tier limits)

**Need help?** Check provider docs or ask in CarbonScope Discord!
