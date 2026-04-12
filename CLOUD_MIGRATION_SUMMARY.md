# Cloud Migration Summary - CarbonScope

## 🎯 Goal
Migrate from local development databases to scalable cloud infrastructure (free tier).

---

## ✅ What You Have Now

### Documentation Created
1. **DATABASE_MIGRATION_GUIDE.md** - PostgreSQL options (Neon, Azure, Supabase)
2. **GRAPH_DATABASE_MIGRATION.md** - Graph DB options (Neo4j, Cosmos DB)
3. **SCALABLE_ARCHITECTURE.md** - Complete multi-database architecture
4. **CLOUD_MIGRATION_SUMMARY.md** - This file

### Setup Scripts Created
1. **scripts/setup-neon.sh** - Neon serverless PostgreSQL
2. **scripts/setup-azure-postgres.sh** - Azure PostgreSQL Flexible Server
3. **scripts/setup-azure-cosmos-graph.sh** - Azure Cosmos DB (Gremlin API)
4. **scripts/setup-neo4j-aura.sh** - Neo4j Aura Free

All scripts are **executable** (`chmod +x`) and **ready to run**.

---

## 🎯 Recommended Stack (100% Free Forever)

```
┌─────────────────────────────────────────────────────────────┐
│                      CarbonScope Cloud                       │
│                     (Free Tier Forever)                      │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Neon         │    │ Neo4j Aura   │    │ Upstash      │
│ PostgreSQL   │    │ Graph DB     │    │ Redis        │
├──────────────┤    ├──────────────┤    ├──────────────┤
│ Serverless   │    │ Property     │    │ Serverless   │
│ Auto-scale   │    │ Graph        │    │ Edge Cache   │
│              │    │              │    │              │
│ FREE TIER:   │    │ FREE TIER:   │    │ FREE TIER:   │
│ • 0.5GB DB   │    │ • 200k nodes │    │ • 10k cmd/day│
│ • 10GB xfer  │    │ • 400k edges │    │ • 256MB      │
│ • No CC req  │    │ • No CC req  │    │ • No CC req  │
└──────────────┘    └──────────────┘    └──────────────┘
```

### Why This Stack?

✅ **$0/month forever**  
✅ **No credit card required** for any service  
✅ **Scales automatically** (pay only when you grow)  
✅ **Best developer experience**  
✅ **Production-ready** (used by thousands of companies)  

---

## 🚀 Quick Start (15 Minutes)

### Step 1: PostgreSQL (Neon)

```bash
cd /path/to/carbonscope-init

# Install Neon CLI
npm install -g neonctl

# Run setup script
./scripts/setup-neon.sh

# Copy connection string to backend/.env
# DATABASE_URL="postgresql://user:pass@ep-xxx.neon.tech/carbonscope?sslmode=require"
```

**Time:** 2-3 minutes  
**Output:** CONNECTION STRING saved to `backend/.env.neon`

---

### Step 2: Graph Database (Neo4j Aura)

```bash
# Run setup script (will guide you through manual signup)
./scripts/setup-neo4j-aura.sh

# Follow on-screen instructions:
# 1. Visit https://neo4j.com/cloud/aura-free/
# 2. Sign up (email/Google/GitHub)
# 3. Create instance
# 4. Save password (shown only once!)
# 5. Enter details in script
```

**Time:** 5-7 minutes  
**Output:** NEO4J_URI and credentials saved to `backend/.env.neo4j`

---

### Step 3: Redis Cache (Upstash)

```bash
# Visit https://upstash.com
# 1. Sign up (free, no CC)
# 2. Create Redis database
# 3. Copy connection string

# Add to backend/.env
echo 'REDIS_URL="redis://default:xxxxx@xxx.upstash.io:6379"' >> backend/.env
```

**Time:** 2-3 minutes  
**Output:** REDIS_URL for caching

---

### Step 4: Update Application

```bash
cd backend

# Install new database drivers
uv add neo4j redis

# Update .env with all connection strings
cat backend/.env.neon backend/.env.neo4j >> backend/.env

# Run migrations
uv run prisma migrate deploy

# Test connections
uv run python -c "
from core.db import test_connections
test_connections()
"
```

**Time:** 3-5 minutes  
**Output:** All databases connected and tested

---

### Step 5: Deploy to Production

```bash
# Option A: Vercel (Frontend) + Railway (Backend)
vercel deploy
railway up

# Option B: Azure (if using Azure Cosmos DB)
az webapp up --name carbonscope-app

# Add environment variables in deployment platform
vercel env add DATABASE_URL production
vercel env add NEO4J_URI production
vercel env add NEO4J_PASSWORD production
vercel env add REDIS_URL production
```

**Time:** 10-15 minutes  
**Output:** Production URLs

---

## 📊 What Each Database Does

### PostgreSQL (Neon)
```sql
-- User data
SELECT * FROM profiles WHERE email = 'user@example.com';

-- Projects
SELECT * FROM projects WHERE user_id = 'xxx';

-- Metadata
SELECT * FROM threads WHERE project_id = 'xxx';
```

**Use Cases:**
- User authentication
- Project metadata
- Settings and preferences
- Transactional data

---

### Neo4j (Graph Database)
```cypher
// Building hierarchy
MATCH (b:Building)-[:CONTAINS*]->(e:Element)
RETURN b, e

// Carbon calculation
MATCH (b:Building {id: 'xxx'})-[:CONTAINS*]->(e:Element)
MATCH (e)-[r:MADE_OF]->(m:Material)
RETURN sum(r.carbon_kg) as total_carbon

// Lifecycle breakdown (EN 15978)
MATCH (e:Element)-[r:MADE_OF]->(m:Material)-[:IN_STAGE]->(s:LifecycleStage)
RETURN s.code, sum(r.carbon_kg) as carbon
ORDER BY s.code
```

**Use Cases:**
- BIM element relationships
- Material composition
- Carbon flow tracking
- Supply chain analysis
- Impact queries

---

### Redis (Upstash)
```bash
# Cache carbon calculation
SET carbon:building-123 '{"total": 15420.5, "stages": {...}}' EX 3600

# Session storage
SET session:user-456 '{"userId": "456", "email": "..."}' EX 86400

# Rate limiting
INCR ratelimit:api:user-456:2024-03-28 EX 86400
```

**Use Cases:**
- LLM response caching (save $$$)
- Session management
- Rate limiting
- Background job queues
- Real-time counters

---

## 💰 Cost Comparison

### Current (Local Docker)
```
Supabase Local: $0 (dev only)
GraphDB Local:  $0 (dev only)
Redis Local:    $0 (dev only)

❌ Not production-ready
❌ No backups
❌ No scaling
❌ No monitoring
```

### Recommended (Cloud Free Tier)
```
Neon:         $0 (0.5GB + 10GB transfer)
Neo4j Aura:   $0 (200k nodes + 400k edges)
Upstash:      $0 (10k commands/day)

✅ Production-ready
✅ Auto-backups
✅ Auto-scaling
✅ Built-in monitoring
✅ 99.9%+ uptime SLA
```

### When You Scale (1000+ Users)
```
Neon Pro:     $19/mo (10GB storage)
Neo4j Pro:    $65/mo (unlimited graph)
Upstash Pro:  $10/mo (1M commands/day)
──────────────────────────
Total:        $94/mo

Still cheaper than self-hosting!
```

---

## 🔧 Alternative: Azure Stack

If you prefer **Microsoft Azure** ecosystem:

```bash
# PostgreSQL
./scripts/setup-azure-postgres.sh

# Graph Database (Cosmos DB with Gremlin API)
./scripts/setup-azure-cosmos-graph.sh

# Redis (Azure Cache for Redis)
az redis create --name carbonscope-cache --resource-group carbonscope-rg
```

**Cost:** FREE for 12 months (Azure Free Tier), then ~$50/month

**When to choose Azure:**
- Already using Azure services
- Enterprise requirements (compliance, private networking)
- Need Azure AD integration
- Want unified billing

---

## 📈 Migration Checklist

### Pre-Migration
- [ ] Read DATABASE_MIGRATION_GUIDE.md
- [ ] Read GRAPH_DATABASE_MIGRATION.md
- [ ] Read SCALABLE_ARCHITECTURE.md
- [ ] Choose database providers

### Migration Steps
- [ ] Create Neon PostgreSQL database
- [ ] Create Neo4j Aura graph database
- [ ] Create Upstash Redis cache
- [ ] Update backend/.env with connection strings
- [ ] Install new database drivers (`uv add neo4j redis`)
- [ ] Run migrations (`prisma migrate deploy`)
- [ ] Test connections

### Data Migration
- [ ] Export local PostgreSQL data (`pg_dump`)
- [ ] Import to Neon (`psql $DATABASE_URL < dump.sql`)
- [ ] Export GraphDB data (RDF/Turtle)
- [ ] Convert RDF to property graph (see scripts)
- [ ] Import to Neo4j (`LOAD CSV` or Python script)
- [ ] Verify data integrity

### Application Updates
- [ ] Update database client initialization
- [ ] Update connection pooling (use serverless drivers)
- [ ] Add error handling for cloud databases
- [ ] Add retry logic for transient failures
- [ ] Update monitoring/logging

### Testing
- [ ] Unit tests pass with new databases
- [ ] Integration tests pass
- [ ] Load testing (simulate production traffic)
- [ ] Carbon calculations match local results
- [ ] Performance benchmarks acceptable

### Deployment
- [ ] Deploy backend to Railway/Azure
- [ ] Deploy frontend to Vercel/Azure
- [ ] Set environment variables in deployment platform
- [ ] Test production endpoints
- [ ] Monitor error rates and performance
- [ ] Set up alerts (Uptime Robot, Sentry)

### Post-Migration
- [ ] Stop local Docker containers
- [ ] Archive local database backups
- [ ] Update team documentation
- [ ] Monitor free tier usage
- [ ] Plan for scaling (set alerts at 80% capacity)

---

## 🆘 Troubleshooting

### Connection Issues

```python
# Test PostgreSQL
import psycopg2
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
print("✅ PostgreSQL connected")

# Test Neo4j
from neo4j import GraphDatabase
driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD"))
)
with driver.session() as session:
    result = session.run("RETURN 1")
    print("✅ Neo4j connected")

# Test Redis
import redis
r = redis.from_url(os.getenv("REDIS_URL"))
r.ping()
print("✅ Redis connected")
```

### Common Errors

**"Connection refused"**
- Check firewall rules (Neon auto-allows, Neo4j requires allowlist)
- Verify connection string format
- Check network connectivity

**"SSL required"**
- Add `?sslmode=require` to PostgreSQL connection string
- Use `neo4j+s://` (not `neo4j://`) for Neo4j

**"Too many connections"**
- Use connection pooling (PgBouncer for Neon)
- Use pooled endpoint for serverless functions

**"Rate limit exceeded"**
- Upgrade to paid tier or optimize queries
- Add caching layer (Redis)

---

## 📚 Next Steps

1. **Start with Neon** (easiest, fastest setup)
2. **Add Neo4j** (when ready to migrate BIM data)
3. **Add Redis** (when you need caching/sessions)
4. **Deploy to production** (Vercel + Railway)
5. **Monitor usage** (stay within free tiers)
6. **Scale gradually** (upgrade tiers as needed)

---

## 🎉 You're Ready!

All scripts and documentation are ready. Just run:

```bash
# 1. PostgreSQL
./scripts/setup-neon.sh

# 2. Graph Database
./scripts/setup-neo4j-aura.sh

# 3. Update application
cd backend && uv add neo4j redis

# 4. Deploy
vercel deploy && railway up
```

**Questions?** Check the detailed guides or ask in CarbonScope Discord!

---

**Created:** March 28, 2026  
**Last Updated:** March 28, 2026  
**Version:** 1.0.0
