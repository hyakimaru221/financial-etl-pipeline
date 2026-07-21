-- ================================================================================
-- 5. Performance Optimization (Indexes for Window Functions)
-- ================================================================================

-- Index for the Partition By clause (Accelerates user history lookup)
CREATE INDEX IF NOT EXISTS idx_transactions_user_id 
ON analytics_transactions(user_id);

-- Index for the Order By and Range clauses (Accelerates time-window heuristics)
CREATE INDEX IF NOT EXISTS idx_transactions_created_at 
ON analytics_transactions(created_at DESC);

-- Composite index for the exact Window Function access pattern
CREATE INDEX IF NOT EXISTS idx_transactions_user_time 
ON analytics_transactions(user_id, created_at DESC);
