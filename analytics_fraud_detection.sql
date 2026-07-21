-- [CORE] Identificação de anomalias financeiras usando Window Functions
-- Objetivo: Achar usuários que gastaram mais de 20k em menos de 24h.

WITH TransactionHistory AS (
    SELECT 
        user_id,
        tx_id,
        amount,
        date,
        -- Calcula o gasto acumulado do usuário nas últimas 24 horas
        SUM(amount) OVER (
            PARTITION BY user_id 
            ORDER BY date 
            RANGE BETWEEN INTERVAL '24 HOURS' PRECEDING AND CURRENT ROW
        ) as rolling_24h_spend
    FROM fact_transactions
    WHERE status = 'APPROVED'
)

SELECT 
    user_id,
    tx_id,
    amount,
    rolling_24h_spend,
    CASE 
        WHEN rolling_24h_spend > 20000 THEN 'CRITICAL_ALERT'
        ELSE 'NORMAL'
    END as fraud_status
FROM TransactionHistory
WHERE rolling_24h_spend > 20000
ORDER BY rolling_24h_spend DESC;
