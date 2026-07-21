import pandas as pd
import requests
import time

# TODO: Migrate hardcoded credentials to AWS Secrets Manager or .env before production deploy
API_ENDPOINT = "https://api.dummy-finance.com/v1/transactions"

def fetch_data_with_backoff(url, max_retries=3):
    """
    Extracts transactional data from the external API.
    Implements exponential backoff to ensure fault tolerance against network drops.
    """
    # Implementation here...

def sanitize_and_flag_payload(df):
    """
    Cleans raw data (handles nulls, type casting) and applies business logic.
    Flags transactions > $10,000 for manual review by the Risk Team.
    """
    # Implementation here...

def load_to_warehouse(df, table_name):
    """
    Upserts data into PostgreSQL. 
    Ensures idempotency by relying on transaction_id as the primary key constraint.
    """
    # Implementation here...
