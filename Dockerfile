# Base image otimizada para produção
FROM python:3.10-slim

# Configuração do diretório de trabalho
WORKDIR /app

# Instalação de dependências (Crie um requirements.txt com: pandas sqlalchemy requests psycopg2-binary)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código fonte para o container
COPY . .

# Comando de execução do pipeline
CMD ["python", "etl_pipeline.py"]
