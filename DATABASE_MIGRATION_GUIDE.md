# Database Migration Guide: Supabase Local → Cloud (Free Tier)

## 🎯 Best Free-Tier Options for CarbonScope

### Recommended: **Neon (Serverless PostgreSQL)** ⭐

**Why Neon:**
- ✅ **Truly free tier**: 0.5 GB storage, 10 GB data transfer/month
- ✅ **Serverless**: Auto-scales, pay only for compute used
- ✅ **PostgreSQL 16**: Latest version, full compatibility
- ✅ **Branching**: Database branching for dev/staging
- ✅ **Zero-downtime migrations**: Built-in migration tools
- ✅ **Global**: Fast from anywhere
- ✅ **No credit card required**

**Free Tier Limits:**
- 0.5 GB storage
- 10 projects
- 10 GB data transfer/month
- Unlimited compute (with limits: 100 hours/month active time)

**Setup Time:** 2 minutes

---

## Alternative Options Comparison

| Provider | Free Tier | PostgreSQL Version | Storage | Best For |
|----------|-----------|-------------------|---------|----------|
| **Neon** ⭐ | Yes (no CC) | 16 | 0.5 GB | Serverless, auto-scaling |
| **Supabase Cloud** | Yes (no CC) | 15 | 500 MB | Full backend (Auth, Storage, Functions) |
| **Azure PostgreSQL** | Yes (12 months) | 16 | 32 GB | Enterprise, Azure ecosystem |
| **Vercel Postgres** | Yes (hobby) | 16 (Neon) | 256 MB | Next.js integration |
| **Railway** | $5 credit | 16 | 1 GB | Docker, full-stack |
| **PlanetScale** | Yes | MySQL 8 | 5 GB | MySQL, branching |
| **Turso** | Yes | SQLite | 9 GB | Edge, global replication |

---

## 🚀 Option 1: Neon (Recommended)

### Step 1: Create Neon Account

```bash
# Visit https://neon.tech and sign up (GitHub/Google/Email)
# Or use Neon CLI
npm install -g neonctl

# Login
neonctl auth

# Create project
neonctl projects create --name carbonscope-prod
```

### Step 2: Get Connection String

Neon provides multiple connection strings:
- **Direct**: For server-side connections
- **Pooled**: For serverless (recommended for Next.js)

Example pooled connection:
```
postgres://user:pass@ep-xxx-yyyy-pooler.us-east-2.aws.neon.tech/carbonscope?sslmode=require
```

### Step 3: Update Environment Variables

**Backend `.env`:**
```env
DATABASE_URL="postgresql://user:pass@ep-xxx.aws.neon.tech/carbonscope?sslmode=require"
DATABASE_POOL_URL="postgresql://user:pass@ep-xxx-pooler.aws.neon.tech/carbonscope?sslmode=require"
```

**Frontend `.env`:**
```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.neon.tech
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### Step 4: Run Migrations

```bash
cd backend

# If using Prisma
npx prisma migrate deploy

# If using SQL migrations
psql $DATABASE_URL < migrations/001_init.sql

# If using Supabase migrations
psql $DATABASE_URL < supabase/migrations/*.sql
```

### Step 5: Test Connection

```bash
# Test database connection
psql $DATABASE_URL -c "SELECT version();"

# Verify tables
psql $DATABASE_URL -c "\dt"
```

---

## 🔷 Option 2: Azure PostgreSQL Flexible Server (Free Tier)

### Prerequisites

```bash
# Login to Azure
az login

# Set subscription (if you have multiple)
az account set --subscription "Your-Subscription-Name"

# Install PostgreSQL extension
az extension add --name db-up
```

### Step 1: Create Resource Group

```bash
# Choose region close to your users
az group create \
  --name carbonscope-rg \
  --location eastus
```

### Step 2: Create PostgreSQL Flexible Server (Free Tier)

```bash
# Free tier: Burstable B1ms (1 vCore, 2 GB RAM, 32 GB storage)
# Available for 12 months free, then $12.41/month

az postgres flexible-server create \
  --resource-group carbonscope-rg \
  --name carbonscope-db \
  --location eastus \
  --admin-user carbonadmin \
  --admin-password 'YourStrongPassword123!' \
  --sku-name Standard_B1ms \
  --tier Burstable \
  --storage-size 32 \
  --version 16 \
  --public-access 0.0.0.0 \
  --yes

# Note: This takes 5-10 minutes
```

### Step 3: Configure Firewall

```bash
# Allow your current IP
MY_IP=$(curl -s ifconfig.me)
az postgres flexible-server firewall-rule create \
  --resource-group carbonscope-rg \
  --name carbonscope-db \
  --rule-name AllowMyIP \
  --start-ip-address $MY_IP \
  --end-ip-address $MY_IP

# Allow Azure services (for deployment)
az postgres flexible-server firewall-rule create \
  --resource-group carbonscope-rg \
  --name carbonscope-db \
  --rule-name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### Step 4: Create Database

```bash
az postgres flexible-server db create \
  --resource-group carbonscope-rg \
  --server-name carbonscope-db \
  --database-name carbonscope_prod
```

### Step 5: Get Connection String

```bash
# Get connection info
az postgres flexible-server show \
  --resource-group carbonscope-rg \
  --name carbonscope-db \
  --query "{FQDN:fullyQualifiedDomainName,User:administratorLogin}" \
  --output table

# Connection string format:
# postgresql://carbonadmin:YourStrongPassword123!@carbonscope-db.postgres.database.azure.com:5432/carbonscope_prod?sslmode=require
```

### Step 6: Update Environment Variables

```env
DATABASE_URL="postgresql://carbonadmin:YourStrongPassword123!@carbonscope-db.postgres.database.azure.com:5432/carbonscope_prod?sslmode=require"
```

---

## 🟢 Option 3: Supabase Cloud (Easiest Migration)

### Step 1: Create Supabase Project

```bash
# Visit https://supabase.com and create account
# Create new project (choose region)
# Wait 2 minutes for provisioning
```

### Step 2: Get Connection Details

Dashboard → Settings → Database:
- **Connection string**: `postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres`
- **API URL**: `https://xxx.supabase.co`
- **Anon Key**: `eyJhbGci...`

### Step 3: Update Environment Variables

```env
# Backend
DATABASE_URL="postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:5432/postgres"

# Frontend
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGci...
```

### Step 4: Run Migrations

```bash
# Push local schema to Supabase
cd supabase
supabase db push --linked

# Or run migrations directly
psql $DATABASE_URL < migrations/*.sql
```

### Benefits
- ✅ **Zero config change** (same as local Supabase)
- ✅ **Auth included** (email, Google, GitHub, etc.)
- ✅ **Storage included** (file uploads)
- ✅ **Realtime** (WebSocket subscriptions)
- ✅ **Edge Functions** (Deno runtime)

---

## 🔄 Migration Steps (From Local Supabase)

### 1. Export Current Data

```bash
cd /path/to/suna-init

# Dump schema
pg_dump -h 127.0.0.1 -p 54321 -U postgres --schema-only > schema.sql

# Dump data
pg_dump -h 127.0.0.1 -p 54321 -U postgres --data-only > data.sql

# Or full backup
pg_dump -h 127.0.0.1 -p 54321 -U postgres > full_backup.sql
```

### 2. Import to New Database

```bash
# Neon/Azure/Supabase Cloud
psql $DATABASE_URL < full_backup.sql

# Or separately
psql $DATABASE_URL < schema.sql
psql $DATABASE_URL < data.sql
```

### 3. Verify Migration

```bash
# Check tables
psql $DATABASE_URL -c "\dt"

# Check row counts
psql $DATABASE_URL -c "SELECT 
  schemaname,
  tablename, 
  n_live_tup as rows
FROM pg_stat_user_tables
ORDER BY n_live_tup DESC;"
```

### 4. Update Application Config

```bash
# Backend
cd backend
# Update .env with new DATABASE_URL
# Test connection
uv run python -c "import os; from sqlalchemy import create_engine; engine = create_engine(os.getenv('DATABASE_URL')); print('Connected:', engine.connect())"

# Frontend
cd apps/frontend
# Update .env with new SUPABASE_URL and keys
# Test in browser
```

### 5. Cleanup Local Supabase

```bash
# Stop local Supabase
cd /path/to/suna-init
supabase stop

# Optional: Remove Docker volumes
docker volume prune
```

---

## 📊 Cost Comparison (After Free Tier)

| Provider | Free Tier | After Free | Best For |
|----------|-----------|------------|----------|
| **Neon** | Forever | $0-$69/mo (usage-based) | Variable traffic |
| **Supabase** | Forever (limited) | $25/mo (Pro) | Auth + Storage needs |
| **Azure** | 12 months | $12.41/mo (B1ms) | Enterprise, compliance |
| **Railway** | $5 credit | $5-$20/mo | Hobby projects |

---

## 🎯 Recommendation for CarbonScope

**Go with Neon** because:

1. ✅ **Serverless** - Auto-scales with usage (carbon tracking = variable load)
2. ✅ **Branching** - Create database branches for dev/staging/prod
3. ✅ **Free tier forever** - No 12-month limit like Azure
4. ✅ **PostgreSQL 16** - Latest features
5. ✅ **Fast setup** - 2 minutes vs 10+ for Azure
6. ✅ **Modern DX** - CLI, GitHub Actions integration
7. ✅ **Zero cold starts** - Unlike serverless compute

**Then add Supabase Cloud for Auth** (free tier):
- Keep auth separate from main DB
- Use Supabase for user management, file storage
- Use Neon for core BIM/carbon data

---

## 🚀 Quick Start: Neon Setup (5 Minutes)

```bash
# 1. Install Neon CLI
npm install -g neonctl

# 2. Authenticate
neonctl auth

# 3. Create project
neonctl projects create --name carbonscope

# 4. Create branches
neonctl branches create --name dev
neonctl branches create --name staging

# 5. Get connection strings
neonctl connection-string main --pooled

# 6. Update .env files
echo "DATABASE_URL=<connection-string>" >> backend/.env

# 7. Run migrations
cd backend
uv run prisma migrate deploy

# 8. Test
uv run python api.py
```

---

## 🔐 Security Best Practices

### Connection Pooling

**For Next.js (serverless):**
```typescript
// lib/db.ts
import { Pool } from '@neondatabase/serverless';

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

export const query = async (text: string, params?: any[]) => {
  const client = await pool.connect();
  try {
    return await client.query(text, params);
  } finally {
    client.release();
  }
};
```

### Environment Variables

**Never commit:**
```bash
# Add to .gitignore
.env.local
.env.production
.env.*.local
```

**Use Vercel/Azure secrets:**
```bash
# Vercel
vercel env add DATABASE_URL

# Azure
az webapp config appsettings set \
  --resource-group carbonscope-rg \
  --name carbonscope-app \
  --settings DATABASE_URL="postgresql://..."
```

---

## 📈 Monitoring

### Neon Dashboard
- Query stats
- Connection pool usage
- Branch sizes
- Autoscaling metrics

### Azure Monitor
```bash
az monitor metrics list \
  --resource carbonscope-db \
  --resource-group carbonscope-rg \
  --metric-names cpu_percent,memory_percent,storage_percent
```

### Prisma Studio (Any DB)
```bash
npx prisma studio
# Opens GUI at http://localhost:5555
```

---

## 🆘 Troubleshooting

### Connection Refused
```bash
# Check firewall rules
# Neon: Auto-allows all IPs (secure by connection string)
# Azure: Must add IP via CLI or portal
az postgres flexible-server firewall-rule list \
  --resource-group carbonscope-rg \
  --name carbonscope-db
```

### SSL Required
```bash
# Always use ?sslmode=require for cloud databases
DATABASE_URL="postgresql://user:pass@host/db?sslmode=require"
```

### Too Many Connections
```bash
# Use connection pooling
# Neon: Use -pooler endpoint
# Azure: Increase max_connections in server parameters
az postgres flexible-server parameter set \
  --resource-group carbonscope-rg \
  --server-name carbonscope-db \
  --name max_connections \
  --value 200
```

---

## Next Steps

1. **Choose provider** (Neon recommended)
2. **Export local data** (`pg_dump`)
3. **Create cloud database**
4. **Import data** (`psql`)
5. **Update environment variables**
6. **Test application**
7. **Remove local Supabase**
8. **Deploy to production**

**Questions?** Check provider docs or ask in Discord!
