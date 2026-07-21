-- ================================================================================
-- Pipeline: Financial Fraud Detection Analytics
-- Description: Cleans raw transactions, ensures idempotency, and flags high-risk data.
-- Engine: PostgreSQL / Amazon Redshift
-- ================================================================================

-- 1. Create mock table for portfolio demonstration purposes
CREATE TABLE IF NOT EXISTS raw_transactions (
    transaction_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50),
    amount DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. CTE to isolate valid transactions and prevent duplicate processing (Idempotency check)
WITH CleanTransactions AS (
    SELECT 
        transaction_id,
        user_id,
        amount,
        created_at,
        -- Using ROW_NUMBER to deduplicate records based on the latest timestamp
        ROW_NUMBER() OVER(PARTITION BY transaction_id ORDER BY created_at DESC) as rn
    FROM raw_transactions
    WHERE amount IS NOT NULL
)

-- 3. Final projection with business logic for the Risk Dashboard
SELECT 
    transaction_id,
    user_id,
    amount,
    created_at,
    CASE 
        WHEN amount > 10000.00 THEN 'HIGH_RISK'
        ELSE 'CLEAN'
    END AS fraud_flag
FROM CleanTransactions
WHERE rn = 1
ORDER BY created_at DESC;
