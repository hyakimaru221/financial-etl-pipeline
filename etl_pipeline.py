import os
import time
import logging
import requests
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.dialects.postgresql import insert

# ==========================================
# ⚙️ PRODUCTION LOGGING CONFIGURATION
# ==========================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ==========================================
# 🔐 ENVIRONMENT VARIABLES (SECURITY & CONFIG)
# ==========================================
DB_CONNECTION_STRING = os.getenv("DATABASE_URL", "postgresql://admin:root@localhost:5432/finance_warehouse")
API_ENDPOINT = os.getenv("API_ENDPOINT", "https://api.coingecko.com/api/v3/exchange_rates" )
MAX_RETRIES = int(os.getenv("ETL_MAX_RETRIES", "5"))
API_TIMEOUT = int(os.getenv("ETL_API_TIMEOUT", "15"))

# ==========================================
# 📡 EXTRACTION LAYER
# ==========================================
def fetch_data_with_backoff(url, max_retries=3, timeout=10):
    """
    Extracts data from external API with exponential backoff for network resilience.
    """
    for attempt in range(max_retries):
        try:
            logging.info(f"Fetching data from {url} (Attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            wait_time = 2 ** attempt
            logging.warning(f"Network error: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    logging.error("Max retries reached. Pipeline extraction failed.")
    raise Exception("API Extraction Failed")

# ==========================================
# 🧹 TRANSFORMATION & BUSINESS LOGIC LAYER
# ==========================================
def sanitize_and_flag_payload(raw_data):
    """
    Cleans raw data, handles nulls, and applies multi-factor fraud heuristics.
    """
    logging.info("Sanitizing payload and applying business logic...")
    
    rates = raw_data.get('rates', {})
    df = pd.DataFrame.from_dict(rates, orient='index')
    
    if df.empty:
        logging.warning("Empty dataframe received.")
        return df

    # Data Cleaning & Type Casting
    df = df.dropna(subset=['value'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    
    # Advanced Business Logic: Flagging based on thresholds and asset types
    # Using .get() to prevent KeyErrors if the API payload structure changes
    df['fraud_flag'] = df.apply(
        lambda row: 'HIGH_RISK' if row['value'] > 10000 or (row['value'] > 5000 and row.get('type') == 'crypto') else 'CLEAN', 
        axis=1
    )
    df['processed_at'] = pd.Timestamp.utcnow()
    
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'currency_code'}, inplace=True)
    
    return df

# ==========================================
# 💾 LOAD LAYER (BATCH UPSERT)
# ==========================================
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

# ==========================================
# 🚀 MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    logging.info("Starting Financial ETL Pipeline...")
    try:
        raw_json = fetch_data_with_backoff(API_ENDPOINT, max_retries=MAX_RETRIES, timeout=API_TIMEOUT)
        clean_df = sanitize_and_flag_payload(raw_json)
        load_to_warehouse_upsert(clean_df, "processed_transactions", DB_CONNECTION_STRING)
        logging.info("Pipeline execution completed successfully.")
    except Exception as err:
        logging.critical(f"Pipeline terminated with errors: {err}")
