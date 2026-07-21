import pandas as pd
import requests
import time
import logging
from sqlalchemy import create_engine

# Configure logging for production monitoring
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# TODO: Migrate to AWS Secrets Manager in production environment
DB_CONNECTION_STRING = "sqlite:///financial_data.db"
API_ENDPOINT = "https://api.coingecko.com/api/v3/exchange_rates"

def fetch_data_with_backoff(url, max_retries=3):
    """
    Extracts data from external API with exponential backoff for network resilience.
    """
    for attempt in range(max_retries):
        try:
            logging.info(f"Fetching data from {url} (Attempt {attempt + 1}/{max_retries})")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            wait_time = 2 ** attempt
            logging.warning(f"Network error: {e}. Retrying in {wait_time} seconds...")
            time.sleep(wait_time)
    
    logging.error("Max retries reached. Pipeline extraction failed.")
    raise Exception("API Extraction Failed")

def sanitize_and_flag_payload(raw_data):
    """
    Cleans raw data, handles nulls, and flags high-value transactions.
    """
    logging.info("Sanitizing payload and applying business logic...")
    
    # Parsing the specific JSON structure
    rates = raw_data.get('rates', {})
    df = pd.DataFrame.from_dict(rates, orient='index')
    
    if df.empty:
        logging.warning("Empty dataframe received.")
        return df

    # Data Cleaning & Type Casting
    df = df.dropna(subset=['value'])
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    
    # Business Logic: Flagging high risk transactions (> 10,000)
    df['fraud_flag'] = df['value'].apply(lambda x: 'HIGH_RISK' if x > 10000 else 'CLEAN')
    df['processed_at'] = pd.Timestamp.utcnow()
    
    # Reset index to structure the final table
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'currency_code'}, inplace=True)
    
    return df

def load_to_warehouse(df, table_name, engine_uri):
    """
    Loads data into the database. Ensures idempotency on ingestion.
    """
    if df.empty:
        logging.info("No data to load. Skipping warehouse ingestion.")
        return

    logging.info(f"Loading {len(df)} records into {table_name}...")
    engine = create_engine(engine_uri)
    
    try:
        # In a real Data Warehouse (Redshift/Snowflake), use UPSERT. 
        # For this local PoC, 'replace' ensures idempotency.
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
        logging.info("Data successfully loaded into the warehouse.")
    except Exception as e:
        logging.error(f"Database insertion failed: {e}")
        raise

if __name__ == "__main__":
    logging.info("Starting Financial ETL Pipeline...")
    try:
        raw_json = fetch_data_with_backoff(API_ENDPOINT)
        clean_df = sanitize_and_flag_payload(raw_json)
        load_to_warehouse(clean_df, "processed_transactions", DB_CONNECTION_STRING)
        logging.info("Pipeline execution completed successfully.")
    except Exception as err:
        logging.critical(f"Pipeline terminated with errors: {err}")
