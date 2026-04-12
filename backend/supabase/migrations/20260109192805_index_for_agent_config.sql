CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_agents_account_carbonscope_default 
    ON agents(account_id) 
    WHERE metadata->>'is_carbonscope_default' = 'true';