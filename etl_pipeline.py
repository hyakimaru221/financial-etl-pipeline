import pandas as pd
import requests
import logging
from sqlalchemy import create_engine
from time import sleep

# Configuração de Log Brutalista
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ETL_CORE] - %(levelname)s - %(message)s')

API_URL = "https://api.mockfinance.com/v1/transactions" # URL Teórica
DB_URI = "postgresql://user:password@localhost:5432/data_warehouse"

def extract_data(endpoint: str, retries: int = 3) -> list:
    """Extração com Exponential Backoff para APIs instáveis."""
    for attempt in range(retries):
        try:
            logging.info(f"Iniciando extração. Tentativa {attempt + 1}/{retries}")
            # Simulação de requisição real
            # response = requests.get(endpoint, timeout=10)
            # response.raise_for_status()
            # return response.json()['data']
            
            # Mock de dados para a Prova de Conceito rodar na tua máquina
            return [
                {"tx_id": "A1", "user_id": 101, "amount": 4500.00, "currency": "BRL", "status": "APPROVED", "date": "2026-07-20T14:30:00Z"},
                {"tx_id": "A2", "user_id": 102, "amount": None, "currency": "USD", "status": "FAILED", "date": "2026-07-20T14:35:00Z"},
                {"tx_id": "A3", "user_id": 101, "amount": 12000.00, "currency": "BRL", "status": "APPROVED", "date": "2026-07-20T14:36:00Z"}
            ]
        except requests.exceptions.RequestException as e:
            logging.warning(f"Falha na rede: {e}. Aguardando {2 ** attempt}s...")
            sleep(2 ** attempt)
    raise Exception("Falha crítica na extração. Pipeline abortado.")

def transform_data(raw_data: list) -> pd.DataFrame:
    """Sanitização e aplicação de regras de negócio."""
    logging.info("Iniciando transformação em memória (Pandas)...")
    df = pd.DataFrame(raw_data)
    
    # 1. Limpeza de Lixo (Drop de nulos críticos)
    df = df.dropna(subset=['amount', 'tx_id'])
    
    # 2. Tipagem Forte
    df['date'] = pd.to_datetime(df['date'])
    df['amount'] = df['amount'].astype(float)
    
    # 3. Regra de Negócio: Flag de Fraude (Transações > 10k num intervalo curto)
    df['is_suspicious'] = df['amount'].apply(lambda x: True if x > 10000 else False)
    
    logging.info(f"Transformação concluída. {len(df)} registros processados.")
    return df

def load_data(df: pd.DataFrame, table_name: str):
    """Carga idempotente no Data Warehouse."""
    logging.info(f"Iniciando carga na tabela {table_name}...")
    engine = create_engine(DB_URI)
    
    # Upsert/Replace para garantir idempotência (se rodar 2x, não duplica)
    try:
        df.to_sql(table_name, engine, if_exists='replace', index=False)
        logging.info("Carga finalizada com sucesso. Banco atualizado.")
    except Exception as e:
        logging.error(f"Erro no banco de dados: {e}")
        raise

if __name__ == "__main__":
    try:
        raw_payload = extract_data(API_URL)
        clean_df = transform_data(raw_data=raw_payload)
        # load_data(clean_df, "fact_transactions") # Descomente quando tiver o Postgres rodando
        print(clean_df.head())
    except Exception as fatal:
        logging.critical(f"PIPELINE MORTO: {fatal}")

