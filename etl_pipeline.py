import os
# ... (mantenha os outros imports) ...

# Environment Variables for Configuration & Security
DB_CONNECTION_STRING = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/finance_db")
API_ENDPOINT = os.getenv("API_ENDPOINT", "https://api.coingecko.com/api/v3/exchange_rates")
MAX_RETRIES = int(os.getenv("ETL_MAX_RETRIES", "3"))
API_TIMEOUT = int(os.getenv("ETL_API_TIMEOUT", "10"))

# ... (mantenha as funções fetch_data_with_backoff e sanitize_and_flag_payload usando as novas variáveis MAX_RETRIES e API_TIMEOUT) ...

def load_to_warehouse_upsert(df, table_name, engine_uri):
    """
    Loads data into PostgreSQL using BATCH UPSERT (ON CONFLICT DO UPDATE).
    Executes a single transaction for the entire dataframe, eliminating row-by-row latency.
    """
    if df.empty:
        logging.info("No data to load. Skipping warehouse ingestion.")
        return

    logging.info(f"Executing BATCH UPSERT for {len(df)} records into {table_name}...")
    engine = create_engine(engine_uri)
    metadata = MetaData()
    
    try:
        target_table = Table(table_name, metadata, autoload_with=engine)
        
        # Base insert statement
        stmt = insert(target_table)
        
        # UPSERT Logic mapped to the target table
        upsert_stmt = stmt.on_conflict_do_update(
            index_elements=['currency_code'],
            set_={
                'value': stmt.excluded.value,
                'fraud_flag': stmt.excluded.fraud_flag,
                'processed_at': stmt.excluded.processed_at
            }
        )
        
        # Executing the statement in a single batch transaction
        with engine.begin() as conn:
            conn.execute(upsert_stmt, df.to_dict(orient='records'))
                
        logging.info("Data successfully BATCH UPSERTED into the warehouse.")
    except Exception as e:
        logging.error(f"Database BATCH UPSERT failed: {e}")
        raise
