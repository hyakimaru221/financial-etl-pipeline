-- ================================================================================
-- Pipeline: Financial Fraud Detection
-- Description: Cleans raw transactions, ensures idempotency, and flags high-risk data.
-- ================================================================================

-- CTE to isolate valid transactions and prevent duplicate processing (Idempotency check)
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

-- Final projection with business logic for the Risk Dashboard
SELECT 
    transaction_id,
    user_id,
    amount,
    CASE 
        WHEN amount > 10000 THEN 'HIGH_RISK'
        ELSE 'CLEAN'
    END AS fraud_flag
FROM CleanTransactions
WHERE rn = 1;
