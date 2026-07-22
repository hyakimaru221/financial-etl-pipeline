-- ================================================================================
-- Pipeline: Financial Fraud Detection Analytics
-- Description: Idempotent ingestion, Velocity-Based Fraud Heuristics, and Indexing.
-- Engine: PostgreSQL / Amazon Redshift
-- ================================================================================

-- ================================================================================
-- 1. DDL: Target Analytics Table
-- ================================================================================
CREATE TABLE IF NOT EXISTS analytics_transactions (
    transaction_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fraud_flag VARCHAR(50)
);

-- ================================================================================
-- 2. TRANSFORMATION: Velocity Heuristics & Idempotency
-- ================================================================================
-- Flags users making more than 3 transactions in a 10-minute window
WITH TransactionVelocity AS (
    SELECT 
        transaction_id,
        user_id,
        amount,
        currency_code,
        created_at,
        COUNT(*) OVER(
            PARTITION BY user_id 
            ORDER BY created_at 
            RANGE BETWEEN INTERVAL '10 minutes' PRECEDING AND CURRENT ROW
        ) as tx_count_10m
    FROM raw_transactions
    WHERE amount IS NOT NULL
),

-- Deduplication to ensure absolute idempotency before UPSERT
CleanTransactions AS (
    SELECT 
        *,
        ROW_NUMBER() OVER(PARTITION BY transaction_id ORDER BY created_at DESC) as rn
    FROM TransactionVelocity
)

-- ================================================================================
-- 3. LOAD: Batch UPSERT (ON CONFLICT DO UPDATE)
-- ================================================================================
INSERT INTO analytics_transactions (transaction_id, user_id, amount, currency_code, created_at, fraud_flag)
SELECT 
    transaction_id,
    user_id,
    amount,
    currency_code,
    created_at,
    CASE 
        WHEN amount > 10000.00 THEN 'HIGH_RISK_AMOUNT'
        WHEN tx_count_10m >= 3 THEN 'HIGH_RISK_VELOCITY'
        ELSE 'CLEAN'
    END AS fraud_flag
FROM CleanTransactions
WHERE rn = 1
ON CONFLICT (transaction_id) 
DO UPDATE SET 
    fraud_flag = EXCLUDED.fraud_flag,
    amount = EXCLUDED.amount;

-- ================================================================================
-- 4. PERFORMANCE: Indexing for Window Functions
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
