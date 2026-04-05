# Database Layer Documentation

## 1. Database Type and Connection

**Database**: PostgreSQL (via Supabase)

**Environment Variables** (from infra/environments/dev/.env.example and core/services/db.py):
- `DATABASE_URL` - Primary database connection string (pooler or direct)
- `DATABASE_POOLER_URL` - Supabase connection pooler URL (port 6543)
- `DATABASE_READ_REPLICA_URL` - Optional read replica for read scaling
- `POSTGRES_PASSWORD` - Fallback if DATABASE_URL not set
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_ANON_KEY` - Supabase anonymous key
- `SUPABASE_SERVICE_ROLE_KEY` - Supabase service role key
- `SUPABASE_JWT_SECRET` - JWT secret for token verification

**Connection Details**:
- Driver: `psycopg` (async PostgreSQL driver)
- Connection format: `postgresql+psycopg://user:password@host:port/database`
- Pooling: AsyncAdaptedQueuePool (pool_size=3, max_overflow=7) or NullPool for Supavisor
- Read replica support: Automatically falls back to primary if replica unavailable

---

## 2. Full Database Schema

### Core Account Management (Basejump Framework)

#### **basejump.accounts**
Multi-tenant account system for SaaS.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Account identifier |
| primary_owner_user_id | UUID | NOT NULL, FK→auth.users | Account owner |
| name | TEXT | | Account name |
| slug | TEXT | UNIQUE | URL-friendly identifier |
| personal_account | BOOLEAN | DEFAULT false | Personal vs team account |
| created_at | TIMESTAMPTZ | | Creation timestamp |
| updated_at | TIMESTAMPTZ | | Last update timestamp |
| created_by | UUID | FK→auth.users | Creator user ID |
| updated_by | UUID | FK→auth.users | Last updater user ID |
| private_metadata | JSONB | DEFAULT '{}' | Internal metadata |
| public_metadata | JSONB | DEFAULT '{}' | Public-facing metadata |

**Relationships**:
- One-to-many with projects, agents, threads, devices, recordings

---

### Agent System

#### **agents**
AI agent configurations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| agent_id | UUID | PRIMARY KEY | Agent identifier |
| account_id | UUID | NOT NULL, FK→basejump.accounts | Owner account |
| name | VARCHAR(255) | NOT NULL | Agent name |
| description | TEXT | | Agent description |
| system_prompt | TEXT | NOT NULL (deprecated) | System instructions |
| configured_mcps | JSONB | DEFAULT '[]' (deprecated) | MCP server configs |
| agentpress_tools | JSONB | DEFAULT '{}' (deprecated) | Tool configurations |
| custom_mcps | JSONB | DEFAULT '[]' | Custom MCP configs |
| is_default | BOOLEAN | DEFAULT false | Default agent flag |
| is_public | BOOLEAN | | Public visibility |
| tags | TEXT[] | | Agent categorization |
| avatar | VARCHAR(10) | (deprecated) | Avatar emoji |
| avatar_color | VARCHAR(7) | (deprecated) | Avatar color hex |
| icon_name | TEXT | | Icon identifier |
| icon_color | TEXT | | Icon color |
| icon_background | TEXT | | Icon background |
| current_version_id | UUID | FK→agent_versions | Active version |
| version_count | INTEGER | DEFAULT 1 | Total versions |
| config | JSONB | DEFAULT '{}' | Unified configuration |
| metadata | JSONB | DEFAULT '{}' | Additional metadata |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Update time |

**Indexes**:
- `idx_agents_account_id` on account_id
- `idx_agents_is_default` on is_default
- `idx_agents_created_at` on created_at
- `idx_agents_current_version` on current_version_id
- `idx_agents_account_default` UNIQUE on (account_id, is_default) WHERE is_default=true

**Note**: Configuration is migrating to unified `config` JSONB field. Legacy columns (system_prompt, configured_mcps, etc.) are deprecated.

---

#### **agent_versions**
Version history for agents.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| version_id | UUID | PRIMARY KEY | Version identifier |
| agent_id | UUID | NOT NULL, FK→agents | Parent agent |
| version_number | INTEGER | NOT NULL | Sequential version |
| version_name | VARCHAR(50) | NOT NULL | Version label |
| system_prompt | TEXT | NOT NULL (deprecated) | System instructions |
| configured_mcps | JSONB | DEFAULT '[]' (deprecated) | MCP configs |
| custom_mcps | JSONB | DEFAULT '[]' | Custom MCP configs |
| agentpress_tools | JSONB | DEFAULT '{}' (deprecated) | Tool configs |
| is_active | BOOLEAN | DEFAULT true | Version active status |
| config | JSONB | DEFAULT '{}' | Unified config snapshot |
| change_description | TEXT | | Version change notes |
| previous_version_id | UUID | FK→agent_versions | Previous version |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Update time |
| created_by | UUID | FK→basejump.accounts | Creator |

**Constraints**:
- UNIQUE(agent_id, version_number)
- UNIQUE(agent_id, version_name)

**Indexes**:
- `idx_agent_versions_agent_id` on agent_id
- `idx_agent_versions_version_number` on version_number
- `idx_agent_versions_is_active` on is_active
- `idx_agent_versions_created_at` on created_at

---

### Project & Thread System (AgentPress)

#### **projects**
Workspaces containing conversation threads.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| project_id | UUID | PRIMARY KEY | Project identifier |
| name | TEXT | NOT NULL | Project name |
| description | TEXT | | Project description |
| account_id | UUID | NOT NULL, FK→basejump.accounts | Owner account |
| sandbox | JSONB | DEFAULT '{}' | Sandbox configuration |
| sandbox_external_id | TEXT | | External sandbox ID |
| sandbox_config | JSONB | | Sandbox metadata |
| is_public | BOOLEAN | DEFAULT false | Public visibility |
| icon_name | TEXT | | Project icon |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Update time |

**Indexes**:
- `idx_projects_account_id` on account_id
- `idx_projects_created_at` on created_at

---

#### **threads**
Conversation threads within projects.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| thread_id | UUID | PRIMARY KEY | Thread identifier |
| account_id | UUID | FK→basejump.accounts | Owner account |
| project_id | UUID | FK→projects | Parent project |
| agent_id | UUID | FK→agents | Agent used (NULL=default) |
| agent_version_id | UUID | FK→agent_versions | Version used |
| is_public | BOOLEAN | DEFAULT false | Public visibility |
| metadata | JSONB | DEFAULT '{}' | Thread metadata |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Update time |

**Indexes**:
- `idx_threads_created_at` on created_at
- `idx_threads_account_id` on account_id
- `idx_threads_project_id` on project_id
- `idx_threads_agent_id` on agent_id
- `idx_threads_agent_version` on agent_version_id

---

#### **messages**
Messages within conversation threads.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| message_id | UUID | PRIMARY KEY | Message identifier |
| thread_id | UUID | NOT NULL, FK→threads | Parent thread |
| type | TEXT | NOT NULL | Message type (user/assistant/system) |
| is_llm_message | BOOLEAN | NOT NULL, DEFAULT true | LLM vs system message |
| content | JSONB | NOT NULL | Message content |
| metadata | JSONB | DEFAULT '{}' | Message metadata |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Update time |

**Indexes**:
- `idx_messages_thread_id` on thread_id
- `idx_messages_created_at` on created_at

---

#### **agent_runs**
Execution sessions for agents.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Run identifier |
| thread_id | UUID | NOT NULL, FK→threads | Associated thread |
| agent_id | UUID | FK→agents | Agent used |
| agent_version_id | UUID | FK→agent_versions | Version used |
| status | TEXT | NOT NULL, DEFAULT 'running' | Run status |
| started_at | TIMESTAMPTZ | DEFAULT NOW() | Start time |
| completed_at | TIMESTAMPTZ | | Completion time |
| error | TEXT | | Error message if failed |
| metadata | JSONB | DEFAULT '{}' | Run metadata |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Update time |

**Status values**: 'running', 'completed', 'failed', 'stopped'

**Indexes**:
- `idx_agent_runs_thread_id` on thread_id
- `idx_agent_runs_status` on status
- `idx_agent_runs_created_at` on created_at

---

### Billing & Credits System

#### **credit_accounts**
User credit balances.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| user_id | UUID | PRIMARY KEY, FK→auth.users | User identifier |
| balance | DECIMAL(12,4) | NOT NULL, DEFAULT 0, CHECK ≥0 | Current balance |
| lifetime_granted | DECIMAL(12,4) | NOT NULL, DEFAULT 0 | Total granted |
| lifetime_purchased | DECIMAL(12,4) | NOT NULL, DEFAULT 0 | Total purchased |
| lifetime_used | DECIMAL(12,4) | NOT NULL, DEFAULT 0 | Total consumed |
| last_grant_at | TIMESTAMPTZ | | Last grant timestamp |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Account creation |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Last update |

---

#### **credit_ledger**
Transaction log for all credit movements.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Transaction ID |
| user_id | UUID | NOT NULL, FK→auth.users | User account |
| amount | DECIMAL(12,4) | NOT NULL | Credit amount (+ or -) |
| balance_after | DECIMAL(12,4) | NOT NULL | Balance after transaction |
| type | TEXT | NOT NULL | Transaction type |
| description | TEXT | | Human-readable description |
| reference_id | UUID | | External reference |
| reference_type | TEXT | | Reference entity type |
| metadata | JSONB | DEFAULT '{}' | Additional data |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Transaction time |
| created_by | UUID | FK→auth.users | Transaction initiator |

**Transaction types**: 'tier_grant', 'purchase', 'admin_grant', 'promotional', 'usage', 'refund', 'adjustment', 'expired'

**Indexes**:
- `idx_credit_ledger_user_id` on (user_id, created_at DESC)
- `idx_credit_ledger_type` on type
- `idx_credit_ledger_reference` on (reference_id, reference_type)

---

#### **credit_grants**
Recurring credit grants tied to subscription tiers.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Grant ID |
| user_id | UUID | NOT NULL, FK→auth.users | Recipient user |
| tier_price_id | TEXT | | Stripe price ID |
| amount | DECIMAL(12,4) | NOT NULL, CHECK >0 | Grant amount |
| granted_at | TIMESTAMPTZ | DEFAULT NOW() | Grant time |
| expires_at | TIMESTAMPTZ | | Expiration time |
| period_start | TIMESTAMPTZ | NOT NULL | Billing period start |
| period_end | TIMESTAMPTZ | NOT NULL | Billing period end |

**Indexes**:
- `idx_credit_grants_user_period` on (user_id, period_start, period_end)

---

### Knowledge Base System

#### **knowledge_base_folders**
Hierarchical folder structure for knowledge entries.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Folder identifier |
| account_id | UUID | NOT NULL, FK→basejump.accounts | Owner account |
| name | TEXT | NOT NULL | Folder name |
| parent_id | UUID | FK→knowledge_base_folders | Parent folder |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Update time |

---

#### **knowledge_base_entries**
Documents and knowledge articles.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Entry identifier |
| account_id | UUID | NOT NULL, FK→basejump.accounts | Owner account |
| folder_id | UUID | FK→knowledge_base_folders | Parent folder |
| title | TEXT | NOT NULL | Entry title |
| content | TEXT | NOT NULL | Entry content |
| file_path | TEXT | | Associated file path |
| file_type | TEXT | | File MIME type |
| metadata | JSONB | DEFAULT '{}' | Additional metadata |
| embedding | vector(1536) | | Vector embedding (pgvector) |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Update time |

**Indexes**:
- `idx_kb_entries_account_folder` on (account_id, folder_id)
- Vector similarity index on embedding (HNSW)

---

#### **agent_knowledge_entry_assignments**
Links agents to knowledge base entries.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Assignment ID |
| agent_id | UUID | NOT NULL, FK→agents | Target agent |
| entry_id | UUID | NOT NULL, FK→knowledge_base_entries | Linked entry |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Assignment time |

**Constraints**:
- UNIQUE(agent_id, entry_id)

---

### Voice & VAPI Integration

#### **vapi_calls**
Voice call session logs.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Call record ID |
| call_id | TEXT | NOT NULL, UNIQUE | VAPI call identifier |
| agent_id | UUID | FK→agents | Agent handling call |
| thread_id | UUID | FK→threads | Associated thread |
| account_id | UUID | NOT NULL, FK→basejump.accounts | Call owner |
| status | TEXT | | Call status |
| duration | INTEGER | | Call duration (seconds) |
| cost | DECIMAL(10,4) | | Call cost |
| metadata | JSONB | DEFAULT '{}' | Call metadata |
| started_at | TIMESTAMPTZ | | Call start time |
| ended_at | TIMESTAMPTZ | | Call end time |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Record creation |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Record update |

---

### Device & Recording System

#### **devices**
Physical or virtual devices for data collection.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Device identifier |
| account_id | UUID | NOT NULL, FK→basejump.accounts | Owner account |
| name | TEXT | | Device name |
| last_seen | TIMESTAMPTZ | | Last activity time |
| is_online | BOOLEAN | DEFAULT false | Online status |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Registration time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Update time |

**Indexes**:
- `idx_devices_account_id` on account_id

---

#### **recordings**
Data recordings from devices.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Recording identifier |
| account_id | UUID | NOT NULL, FK→basejump.accounts | Owner account |
| device_id | UUID | NOT NULL, FK→devices | Source device |
| name | TEXT | | Recording name |
| preprocessed_file_path | TEXT | | Processed file path |
| raw_data_file_path | TEXT | | Raw data path |
| metadata_file_path | TEXT | | Metadata path |
| audio_file_path | TEXT | | Audio data path |
| a11y_file_path | TEXT | | Accessibility data |
| action_training_file_path | TEXT | | Training data path |
| meta | JSONB | | Recording metadata |
| ui_annotated | BOOLEAN | DEFAULT false | UI annotation flag |
| action_annotated | BOOLEAN | DEFAULT false | Action annotation flag |
| created_at | TIMESTAMPTZ | DEFAULT NOW() | Creation time |
| updated_at | TIMESTAMPTZ | DEFAULT NOW() | Update time |

**Indexes**:
- `idx_recordings_account_id` on account_id
- `idx_recordings_device_id` on device_id

---

### Additional Tables (Summary)

**Agent Triggers**:
- `agent_triggers` - Trigger configurations for agents
- `trigger_events` - Trigger execution logs
- `oauth_installations` - OAuth app installations

**Workflows**:
- `agent_workflows` - Step-by-step task workflows
- `workflow_steps` - Individual workflow steps
- `workflow_executions` - Workflow execution history
- `workflow_step_executions` - Step-level execution logs

**File Management**:
- `file_uploads` - User-uploaded files
- `staged_files` - Temporary file staging

**User Management**:
- `user_roles` - User role assignments (admin, etc.)
- `user_presence` - Real-time user presence
- `user_memories` - Long-term user memory storage

**Monitoring & Analytics**:
- `conversation_analytics` - Thread usage analytics
- `vercel_analytics_daily` - Daily visitor metrics
- `feedback` - User feedback submissions

---

## 3. Data Flows Per User Action

### **Action 1: User Creates New Agent**

**Frontend**: POST /agents
**Backend**: `core/agents/agent_crud.py::create_agent_endpoint()`

**Records Created**:
1. **agents** table:
   ```sql
   INSERT INTO agents (
     account_id, name, description, icon_name, icon_color,
     icon_background, is_default, version_count, metadata
   ) VALUES (...)
   RETURNING agent_id
   ```

2. **agent_versions** table (first version):
   ```sql
   INSERT INTO agent_versions (
     agent_id, version_number, version_name, config, created_by
   ) VALUES (:agent_id, 1, 'v1', :config, :account_id)
   RETURNING version_id
   ```

3. **agents** table (update with current_version_id):
   ```sql
   UPDATE agents
   SET current_version_id = :version_id, version_count = 1
   WHERE agent_id = :agent_id
   ```

**Tables Affected**: `agents` (INSERT + UPDATE), `agent_versions` (INSERT)

---

### **Action 2: User Sends Message to Agent**

**Frontend**: POST /threads/{thread_id}/messages
**Backend**: `core/agents/api.py::stream_agent_response()`

**Records Created/Updated**:
1. **messages** table (user message):
   ```sql
   INSERT INTO messages (thread_id, type, is_llm_message, content, metadata)
   VALUES (:thread_id, 'user', false, :content, '{}')
   RETURNING message_id
   ```

2. **agent_runs** table (execution session):
   ```sql
   INSERT INTO agent_runs (thread_id, agent_id, agent_version_id, status, started_at, metadata)
   VALUES (:thread_id, :agent_id, :version_id, 'running', NOW(), :metadata)
   RETURNING id
   ```

3. **messages** table (assistant response):
   ```sql
   INSERT INTO messages (thread_id, type, is_llm_message, content, metadata)
   VALUES (:thread_id, 'assistant', true, :response, :tool_calls)
   RETURNING message_id
   ```

4. **agent_runs** table (completion):
   ```sql
   UPDATE agent_runs
   SET status = 'completed', completed_at = NOW()
   WHERE id = :agent_run_id
   ```

5. **credit_accounts** + **credit_ledger** (deduct credits):
   ```sql
   -- Via deduct_credits() function
   UPDATE credit_accounts
   SET balance = balance - :cost, lifetime_used = lifetime_used + :cost
   WHERE user_id = :user_id

   INSERT INTO credit_ledger (user_id, amount, balance_after, type, description)
   VALUES (:user_id, -:cost, :new_balance, 'usage', 'Agent message')
   ```

6. **threads** table (update timestamp):
   ```sql
   UPDATE threads SET updated_at = NOW() WHERE thread_id = :thread_id
   ```

**Tables Affected**: `messages` (2 INSERTs), `agent_runs` (INSERT + UPDATE), `credit_accounts` (UPDATE), `credit_ledger` (INSERT), `threads` (UPDATE)

---

### **Action 3: User Creates New Project**

**Frontend**: POST /projects
**Backend**: `core/threads/api.py::create_project()`

**Records Created**:
1. **projects** table:
   ```sql
   INSERT INTO projects (account_id, name, description, icon_name, is_public)
   VALUES (:account_id, :name, :description, :icon_name, :is_public)
   RETURNING project_id
   ```

**Tables Affected**: `projects` (INSERT)

---

### **Action 4: User Creates Thread in Project**

**Frontend**: POST /threads
**Backend**: `core/threads/api.py::create_thread()`

**Records Created**:
1. **threads** table:
   ```sql
   INSERT INTO threads (account_id, project_id, agent_id, agent_version_id, metadata)
   VALUES (:account_id, :project_id, :agent_id, :version_id, :metadata)
   RETURNING thread_id
   ```

2. **projects** table (update timestamp):
   ```sql
   UPDATE projects SET updated_at = NOW() WHERE project_id = :project_id
   ```

**Tables Affected**: `threads` (INSERT), `projects` (UPDATE)

---

### **Action 5: User Purchases Credits**

**Frontend**: POST /billing/credits/purchase (via Stripe)
**Backend**: Stripe webhook → `core/billing/api.py::stripe_webhook()`

**Records Created**:
1. **credit_purchases** table:
   ```sql
   INSERT INTO credit_purchases (
     user_id, stripe_payment_intent_id, amount, price_usd, status
   ) VALUES (:user_id, :payment_intent_id, :credits, :price, 'completed')
   RETURNING id
   ```

2. **credit_accounts** table:
   ```sql
   -- Create if not exists
   INSERT INTO credit_accounts (user_id, balance, lifetime_purchased)
   VALUES (:user_id, :credits, :credits)
   ON CONFLICT (user_id) DO UPDATE
   SET balance = credit_accounts.balance + :credits,
       lifetime_purchased = credit_accounts.lifetime_purchased + :credits
   ```

3. **credit_ledger** table:
   ```sql
   INSERT INTO credit_ledger (
     user_id, amount, balance_after, type, description, reference_id, reference_type
   ) VALUES (
     :user_id, :credits, :new_balance, 'purchase',
     'Credit purchase', :purchase_id, 'credit_purchase'
   )
   ```

**Tables Affected**: `credit_purchases` (INSERT), `credit_accounts` (UPSERT), `credit_ledger` (INSERT)

---

### **Action 6: User Uploads File to Knowledge Base**

**Frontend**: POST /knowledge-base/upload
**Backend**: `core/knowledge_base/api.py::upload_knowledge_file()`

**Records Created**:
1. **file_uploads** table:
   ```sql
   INSERT INTO file_uploads (account_id, file_name, file_path, file_type, file_size)
   VALUES (:account_id, :filename, :storage_path, :mime_type, :size)
   RETURNING id
   ```

2. **knowledge_base_entries** table:
   ```sql
   INSERT INTO knowledge_base_entries (
     account_id, folder_id, title, content, file_path, file_type, embedding
   ) VALUES (
     :account_id, :folder_id, :title, :extracted_text,
     :file_path, :mime_type, :vector_embedding
   )
   RETURNING id
   ```

3. **agent_knowledge_entry_assignments** table (if assigning to agent):
   ```sql
   INSERT INTO agent_knowledge_entry_assignments (agent_id, entry_id)
   VALUES (:agent_id, :entry_id)
   ```

**Tables Affected**: `file_uploads` (INSERT), `knowledge_base_entries` (INSERT), `agent_knowledge_entry_assignments` (INSERT if assigned)

---

### **Action 7: User Updates Agent Configuration**

**Frontend**: PUT /agents/{agent_id}
**Backend**: `core/agents/agent_crud.py::update_agent_endpoint()`

**Records Created/Updated**:
1. **agents** table:
   ```sql
   UPDATE agents
   SET name = :name, description = :description,
       icon_name = :icon_name, icon_color = :icon_color,
       metadata = :metadata, updated_at = NOW()
   WHERE agent_id = :agent_id AND account_id = :account_id
   ```

2. **agent_versions** table (new version if config changed):
   ```sql
   INSERT INTO agent_versions (
     agent_id, version_number, version_name, config,
     previous_version_id, change_description
   ) VALUES (
     :agent_id, :next_version_num, 'v' || :next_version_num,
     :new_config, :current_version_id, :changes
   )
   RETURNING version_id
   ```

3. **agents** table (update current version):
   ```sql
   UPDATE agents
   SET current_version_id = :new_version_id,
       version_count = version_count + 1
   WHERE agent_id = :agent_id
   ```

**Tables Affected**: `agents` (2 UPDATEs), `agent_versions` (INSERT)

---

### **Action 8: User Deletes Thread**

**Frontend**: DELETE /threads/{thread_id}
**Backend**: `core/threads/api.py::delete_thread()`

**Records Deleted**:
1. **agent_runs** table (CASCADE from thread_id FK):
   ```sql
   DELETE FROM agent_runs WHERE thread_id = :thread_id
   ```

2. **messages** table (CASCADE from thread_id FK):
   ```sql
   DELETE FROM messages WHERE thread_id = :thread_id
   ```

3. **threads** table:
   ```sql
   DELETE FROM threads WHERE thread_id = :thread_id AND account_id = :account_id
   RETURNING thread_id
   ```

4. **projects** table (update timestamp):
   ```sql
   UPDATE projects SET updated_at = NOW() WHERE project_id = :project_id
   ```

**Tables Affected**: `agent_runs` (DELETE), `messages` (DELETE), `threads` (DELETE), `projects` (UPDATE)

---

## 4. Validation Queries

### **Validation 1: Verify Agent Created**
```sql
SELECT
    a.agent_id,
    a.name,
    a.account_id,
    a.current_version_id,
    av.version_number,
    av.version_name
FROM agents a
LEFT JOIN agent_versions av ON a.current_version_id = av.version_id
WHERE a.agent_id = :agent_id AND a.account_id = :account_id;
```

**Expected**: 1 row with matching agent_id and version_number = 1

---

### **Validation 2: Verify Message & Agent Run Completed**
```sql
-- Check user message created
SELECT message_id, type, content
FROM messages
WHERE thread_id = :thread_id AND type = 'user'
ORDER BY created_at DESC LIMIT 1;

-- Check assistant response created
SELECT message_id, type, content
FROM messages
WHERE thread_id = :thread_id AND type = 'assistant'
ORDER BY created_at DESC LIMIT 1;

-- Check agent run completed
SELECT id, status, completed_at, error
FROM agent_runs
WHERE thread_id = :thread_id
ORDER BY started_at DESC LIMIT 1;

-- Verify credit deduction
SELECT amount, type, description, balance_after
FROM credit_ledger
WHERE user_id = :user_id AND type = 'usage'
ORDER BY created_at DESC LIMIT 1;
```

**Expected**:
- 2 messages (user + assistant)
- 1 agent_run with status='completed' and completed_at NOT NULL
- 1 credit_ledger entry with negative amount

---

### **Validation 3: Verify Project & Thread Created**
```sql
-- Check project exists
SELECT project_id, name, account_id, created_at
FROM projects
WHERE project_id = :project_id AND account_id = :account_id;

-- Check thread exists and linked to project
SELECT thread_id, project_id, account_id, agent_id, created_at
FROM threads
WHERE thread_id = :thread_id AND project_id = :project_id;

-- Verify project updated timestamp
SELECT updated_at FROM projects WHERE project_id = :project_id;
```

**Expected**:
- 1 project row
- 1 thread row with correct project_id
- projects.updated_at >= threads.created_at

---

### **Validation 4: Verify Credit Purchase**
```sql
-- Check purchase recorded
SELECT id, amount, price_usd, status
FROM credit_purchases
WHERE user_id = :user_id AND stripe_payment_intent_id = :payment_intent_id;

-- Check credit balance updated
SELECT user_id, balance, lifetime_purchased
FROM credit_accounts
WHERE user_id = :user_id;

-- Check ledger entry
SELECT amount, balance_after, type, description
FROM credit_ledger
WHERE user_id = :user_id AND reference_type = 'credit_purchase'
ORDER BY created_at DESC LIMIT 1;
```

**Expected**:
- 1 credit_purchase with status='completed'
- credit_accounts.balance increased by purchase amount
- 1 credit_ledger entry with type='purchase' and positive amount

---

### **Validation 5: Verify Knowledge Base Upload**
```sql
-- Check file uploaded
SELECT id, file_name, file_path, file_type, account_id
FROM file_uploads
WHERE account_id = :account_id
ORDER BY created_at DESC LIMIT 1;

-- Check knowledge entry created with embedding
SELECT id, title, content, file_path, embedding IS NOT NULL as has_embedding
FROM knowledge_base_entries
WHERE account_id = :account_id
ORDER BY created_at DESC LIMIT 1;

-- Check agent assignment (if applicable)
SELECT agent_id, entry_id
FROM agent_knowledge_entry_assignments
WHERE entry_id = :entry_id;
```

**Expected**:
- 1 file_upload row
- 1 knowledge_base_entries row with has_embedding=true
- 0 or 1 agent assignment rows

---

### **Validation 6: Verify Agent Update & Versioning**
```sql
-- Check agent updated
SELECT agent_id, name, description, version_count, current_version_id, updated_at
FROM agents
WHERE agent_id = :agent_id;

-- Check new version created
SELECT version_id, version_number, version_name, previous_version_id, change_description
FROM agent_versions
WHERE agent_id = :agent_id
ORDER BY version_number DESC LIMIT 1;

-- Verify version count matches
SELECT
    a.version_count,
    COUNT(av.version_id) as actual_versions
FROM agents a
LEFT JOIN agent_versions av ON a.agent_id = av.agent_id
WHERE a.agent_id = :agent_id
GROUP BY a.version_count;
```

**Expected**:
- agents.updated_at recently changed
- agents.version_count incremented
- New agent_versions row with incremented version_number
- version_count = actual_versions

---

### **Validation 7: Verify Thread Deletion Cascade**
```sql
-- Check thread deleted
SELECT COUNT(*) as thread_exists
FROM threads
WHERE thread_id = :thread_id;

-- Check messages deleted (CASCADE)
SELECT COUNT(*) as message_count
FROM messages
WHERE thread_id = :thread_id;

-- Check agent runs deleted (CASCADE)
SELECT COUNT(*) as run_count
FROM agent_runs
WHERE thread_id = :thread_id;

-- Verify project timestamp updated
SELECT updated_at
FROM projects
WHERE project_id = :project_id;
```

**Expected**:
- thread_exists = 0
- message_count = 0
- run_count = 0
- projects.updated_at >= deletion timestamp

---

### **Validation 8: Check User Credit Balance**
```sql
SELECT
    user_id,
    balance,
    lifetime_granted,
    lifetime_purchased,
    lifetime_used,
    (lifetime_granted + lifetime_purchased - lifetime_used) as calculated_balance,
    last_grant_at
FROM credit_accounts
WHERE user_id = :user_id;
```

**Expected**: balance = calculated_balance (integrity check)

---

### **Validation 9: Check Active Agent Runs**
```sql
SELECT
    ar.id as run_id,
    ar.thread_id,
    ar.status,
    ar.started_at,
    EXTRACT(EPOCH FROM (NOW() - ar.started_at)) as runtime_seconds,
    t.account_id,
    a.name as agent_name
FROM agent_runs ar
JOIN threads t ON ar.thread_id = t.thread_id
LEFT JOIN agents a ON ar.agent_id = a.agent_id
WHERE ar.status = 'running' AND t.account_id = :account_id
ORDER BY ar.started_at DESC;
```

**Expected**: Shows currently running agents for debugging

---

### **Validation 10: Verify Account Isolation (RLS)**
```sql
-- This should return 0 when run as user A trying to access user B's data
SELECT COUNT(*) as unauthorized_access
FROM agents
WHERE agent_id = :agent_id_from_user_b;

-- Expected result when RLS working: 0
-- If RLS broken: > 0 (security issue)
```

**Expected**: 0 rows (RLS blocking cross-account access)

---

## Summary

**Database**: PostgreSQL via Supabase
**Connection Variable**: `DATABASE_URL` or `DATABASE_POOLER_URL`
**Core Tables**: 20+ tables including agents, threads, messages, projects, credit system
**Primary Keys**: All UUIDs with gen_random_uuid()
**Security**: Row Level Security (RLS) enabled on all multi-tenant tables
**Search**: pgvector for semantic search on knowledge base
**Relationships**: Strong FK constraints with CASCADE deletes

All user actions follow consistent patterns:
1. INSERT new records with UUIDs
2. UPDATE related timestamps
3. Log transactions (credit_ledger, agent runs)
4. CASCADE deletes maintain referential integrity
