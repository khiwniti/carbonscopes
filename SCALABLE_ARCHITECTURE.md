# CarbonScope Scalable Cloud Architecture

## 🎯 Production-Ready Multi-Database Architecture

### Current (Local Dev)
```
┌─────────────────┐
│ Supabase Local  │ ← PostgreSQL + Auth (port 54321)
└─────────────────┘
         ↓
┌─────────────────┐
│ GraphDB Local   │ ← RDF/SPARQL (port 7200)
└─────────────────┘
         ↓
┌─────────────────┐
│ Redis Local     │ ← Cache (port 6379)
└─────────────────┘
```

### Recommended (Cloud - Free Tier)
```
┌──────────────────────────────────────────────────────────┐
│                     CarbonScope Cloud                     │
└──────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Neon         │    │ Neo4j Aura   │    │ Upstash      │
│ PostgreSQL   │    │ Graph DB     │    │ Redis        │
├──────────────┤    ├──────────────┤    ├──────────────┤
│ • Users      │    │ • Buildings  │    │ • Sessions   │
│ • Projects   │    │ • Elements   │    │ • LLM cache  │
│ • Auth       │    │ • Materials  │    │ • Rate limit │
│ • Settings   │    │ • Carbon     │    │ • Job queue  │
│ • Metadata   │    │ • Lifecycles │    │              │
│              │    │              │    │              │
│ FREE:        │    │ FREE:        │    │ FREE:        │
│ 0.5GB        │    │ 200k nodes   │    │ 10k cmds/day │
│ 10GB/month   │    │ 400k edges   │    │ 256MB        │
└──────────────┘    └──────────────┘    └──────────────┘
```

---

## 📊 Database Responsibilities

### PostgreSQL (Neon) - Structured Data
```
profiles
├── id (uuid)
├── email (text)
├── full_name (text)
├── avatar_url (text)
└── created_at (timestamp)

projects
├── id (uuid)
├── user_id (uuid) → profiles
├── name (text)
├── description (text)
├── building_ids (jsonb)  ← Reference to graph
└── created_at (timestamp)

agents
├── id (uuid)
├── user_id (uuid)
├── name (text)
├── model (text)
├── tools (jsonb)
└── config (jsonb)

threads
├── id (uuid)
├── user_id (uuid)
├── agent_id (uuid)
├── project_id (uuid)
├── messages (jsonb)
└── metadata (jsonb)
```

**Use for:**
- ✅ User authentication
- ✅ CRUD operations
- ✅ Transactional data
- ✅ Simple queries (by ID, user_id)
- ✅ Metadata storage

---

### Neo4j Aura - BIM Relationships
```
(:Building {id, name, location, ifc_guid})
    ↓ [:CONTAINS]
(:Floor {id, name, level, height})
    ↓ [:CONTAINS]
(:Space {id, name, area, volume})
    ↓ [:CONTAINS]
(:Element {id, name, type, ifc_class, volume})
    ↓ [:MADE_OF {quantity, unit}]
(:Material {id, name, carbon_factor})
    ↓ [:IN_STAGE]
(:LifecycleStage {code, name, description})
    ↑ [:EMITS {carbon_kg, source}]
    └─ Carbon emission data
```

**Use for:**
- ✅ BIM hierarchies (Building → Floor → Element)
- ✅ Material composition (Element → Material)
- ✅ Carbon calculations (traversing entire building)
- ✅ Lifecycle analysis (EN 15978 stages)
- ✅ Supply chain tracking (Material → Supplier → Transport)
- ✅ Impact queries ("Which materials contribute most to stage A1-A3?")

---

### Redis (Upstash) - Caching & Queues
```
Key Patterns:
- session:{user_id}              → User session
- llm:cache:{hash}               → LLM response cache
- carbon:calc:{building_id}      → Cached carbon total
- ratelimit:{user_id}:{endpoint} → API rate limiting
- job:{job_id}                   → Background job status
```

**Use for:**
- ✅ Session storage
- ✅ LLM response caching (save API costs)
- ✅ Rate limiting
- ✅ Background job queues (IFC parsing, carbon calc)
- ✅ Real-time counters

---

## 🔄 Data Flow Examples

### Example 1: Create New Building Project

```typescript
// 1. Create project in PostgreSQL
const project = await neon.query(`
  INSERT INTO projects (id, user_id, name, description)
  VALUES ($1, $2, $3, $4)
  RETURNING *
`, [projectId, userId, 'Office Building', 'Net-zero carbon target']);

// 2. Create building node in Neo4j
await neo4j.run(`
  CREATE (b:Building {
    id: $projectId,
    name: $name,
    location: $location,
    created_at: datetime()
  })
  RETURN b
`, { projectId, name: 'Office Building', location: 'San Francisco' });

// 3. Cache building ID in Redis
await redis.set(`project:${projectId}:building_id`, projectId);
```

---

### Example 2: Calculate Building Carbon Footprint

```typescript
// 1. Check cache first
const cached = await redis.get(`carbon:${buildingId}`);
if (cached) return JSON.parse(cached);

// 2. Query graph database for carbon calculation
const result = await neo4j.run(`
  MATCH (b:Building {id: $buildingId})-[:CONTAINS*]->(e:Element)
  MATCH (e)-[r:MADE_OF]->(m:Material)-[:IN_STAGE]->(s:LifecycleStage)
  RETURN 
    b.name as building_name,
    s.code as lifecycle_stage,
    sum(r.quantity * m.carbon_factor) as total_carbon_kg
  ORDER BY s.code
`, { buildingId });

// 3. Store result in PostgreSQL for reporting
await neon.query(`
  INSERT INTO carbon_reports (building_id, lifecycle_data, total, calculated_at)
  VALUES ($1, $2, $3, NOW())
`, [buildingId, result, total]);

// 4. Cache for 1 hour
await redis.setex(`carbon:${buildingId}`, 3600, JSON.stringify(result));

return result;
```

---

### Example 3: Upload IFC File & Parse

```typescript
// 1. Store file metadata in PostgreSQL
const fileRecord = await neon.query(`
  INSERT INTO files (id, project_id, filename, size, status)
  VALUES ($1, $2, $3, $4, 'processing')
  RETURNING *
`, [fileId, projectId, 'building.ifc', fileSize]);

// 2. Queue background job in Redis
await redis.lpush('ifc:parsing:queue', JSON.stringify({
  fileId,
  projectId,
  buildingId,
  url: fileUrl
}));

// 3. Worker processes IFC file
// ... parse IFC entities ...

// 4. Create graph structure in Neo4j
for (const element of ifcElements) {
  await neo4j.run(`
    MATCH (b:Building {id: $buildingId})
    CREATE (b)-[:CONTAINS]->(e:Element {
      id: $elementId,
      ifc_guid: $ifcGuid,
      ifc_class: $ifcClass,
      name: $name,
      volume: $volume
    })
  `, { buildingId, elementId, ...element });
}

// 5. Update file status in PostgreSQL
await neon.query(`
  UPDATE files SET status = 'completed', processed_at = NOW()
  WHERE id = $1
`, [fileId]);
```

---

## 🚀 Setup Instructions

### Quick Start (All Free Tiers)

```bash
# 1. PostgreSQL (Neon)
./scripts/setup-neon.sh
# → Get DATABASE_URL

# 2. Graph Database (Neo4j Aura)
./scripts/setup-neo4j-aura.sh
# → Get NEO4J_URI, NEO4J_PASSWORD

# 3. Redis (Upstash) - Visit https://upstash.com
# → Create Redis database
# → Get REDIS_URL

# 4. Update backend/.env
cat > backend/.env << EOF
# PostgreSQL
DATABASE_URL="postgresql://user:pass@ep-xxx.neon.tech/carbonscope"

# Neo4j Graph
NEO4J_URI="neo4j+s://xxxxx.databases.neo4j.io"
NEO4J_USER="neo4j"
NEO4J_PASSWORD="your-password"

# Redis
REDIS_URL="redis://default:xxxxx@xxx.upstash.io:6379"

# Auth (Supabase Cloud or Clerk)
NEXT_PUBLIC_SUPABASE_URL="https://xxx.supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="eyJhbG..."
EOF

# 5. Install dependencies
cd backend
uv add neo4j gremlinpython redis

# 6. Run migrations
uv run prisma migrate deploy

# 7. Start backend
uv run python api.py
```

---

## 💰 Cost Breakdown (Free Forever)

| Service | Free Tier | Upgrade Cost | When to Upgrade |
|---------|-----------|--------------|-----------------|
| **Neon** | 0.5GB, 10GB transfer | $19/mo (10GB) | >1000 users |
| **Neo4j Aura** | 200k nodes, 400k edges | $65/mo (unlimited) | >100 buildings |
| **Upstash Redis** | 10k cmds/day, 256MB | $10/mo (1M cmds) | >1000 users |
| **Supabase** | 500MB, 50k auth users | $25/mo (8GB) | >1000 users |
| **Total** | **$0/month** | **~$119/month** | After scaling |

---

## 📈 Scaling Strategy

### Phase 1: MVP (Free Tier) - 0-100 Users
```
Neon Free        → 10 buildings
Neo4j Aura Free  → 100 buildings  
Upstash Free     → Cache + sessions
Deploy: Vercel   → Free tier (Next.js)
Deploy: Railway  → Free tier (Python backend)
```

### Phase 2: Growth ($50-100/mo) - 100-1000 Users
```
Neon Pro         → $19/mo
Neo4j Aura Pro   → $65/mo
Upstash Pro      → $10/mo
Vercel Pro       → $20/mo
Railway Pro      → $20/mo
─────────────────────────
Total: ~$134/mo
```

### Phase 3: Scale ($500-1000/mo) - 1000-10,000 Users
```
Azure/AWS        → Managed services
Kubernetes       → Container orchestration
CDN              → CloudFlare Enterprise
Monitoring       → Datadog/New Relic
```

---

## 🔐 Security Best Practices

### Database Access
```python
# backend/core/db.py
from contextlib import asynccontextmanager

class DatabaseManager:
    def __init__(self):
        self.postgres = PostgresPool(os.getenv("DATABASE_URL"))
        self.neo4j = Neo4jDriver(
            os.getenv("NEO4J_URI"),
            auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
        )
        self.redis = Redis.from_url(os.getenv("REDIS_URL"))
    
    @asynccontextmanager
    async def transaction(self):
        """Distributed transaction across PostgreSQL + Neo4j"""
        async with self.postgres.transaction() as pg_tx:
            try:
                with self.neo4j.session() as neo_tx:
                    yield (pg_tx, neo_tx)
                    # Commit both if no errors
                    await pg_tx.commit()
                    neo_tx.commit()
            except Exception:
                # Rollback both on error
                await pg_tx.rollback()
                neo_tx.rollback()
                raise
```

### Environment Variables
```bash
# Never commit these!
# Use Vercel/Railway secrets
vercel env add DATABASE_URL production
vercel env add NEO4J_PASSWORD production
railway variables set DATABASE_URL=$DATABASE_URL
```

---

## 📊 Monitoring & Observability

### Metrics to Track
```typescript
// backend/core/metrics.ts
import { Counter, Histogram } from 'prom-client';

export const metrics = {
  // PostgreSQL
  postgres_queries: new Counter({
    name: 'postgres_queries_total',
    help: 'Total PostgreSQL queries',
    labelNames: ['table', 'operation']
  }),
  
  // Neo4j
  neo4j_traversals: new Histogram({
    name: 'neo4j_traversal_duration_seconds',
    help: 'Neo4j traversal duration',
    labelNames: ['query_type']
  }),
  
  // Redis
  redis_cache_hits: new Counter({
    name: 'redis_cache_hits_total',
    help: 'Redis cache hits vs misses',
    labelNames: ['hit']
  }),
  
  // Carbon calculations
  carbon_calculations: new Counter({
    name: 'carbon_calculations_total',
    help: 'Total carbon calculations',
    labelNames: ['building_type']
  })
};
```

### Dashboards
- **Neon**: Built-in metrics dashboard
- **Neo4j**: Query performance in Aura Console
- **Upstash**: Request metrics in dashboard
- **Custom**: Grafana + Prometheus for unified view

---

## 🎯 Next Steps

1. **Run setup scripts** for chosen databases
2. **Update environment variables** in backend/.env
3. **Test connections** with sample queries
4. **Migrate sample data** (10 buildings)
5. **Deploy to production** (Vercel + Railway)
6. **Monitor usage** (stay within free tiers)
7. **Scale** when needed (upgrade tiers)

---

## 📚 Additional Resources

- [Neon Documentation](https://neon.tech/docs)
- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/)
- [Azure Cosmos DB Gremlin](https://learn.microsoft.com/en-us/azure/cosmos-db/gremlin/)
- [Upstash Redis](https://docs.upstash.com/redis)
- [BIM/IFC Standards](https://technical.buildingsmart.org/)
- [EN 15978 Lifecycle](https://www.en-standard.eu/bs-en-15978-2011-sustainability-of-construction-works-assessment-of-environmental-performance-of-buildings-calculation-method/)

**Questions?** Check CarbonScope docs or ask in Discord!
