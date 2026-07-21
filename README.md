# 🚀 Financial Data Pipeline: ETL & Fraud Detection

## 👁️ Visão Geral
Pipeline de Engenharia de Dados construído para extrair, sanitizar e modelar transações financeiras em tempo real. O foco da arquitetura é **Idempotência**, **Resiliência de Rede (Exponential Backoff)** e **Otimização de Custos em Cloud**.

## ⚙️ Stack Tecnológica
- **Extração & Transformação:** Python (Pandas, Requests)
- **Armazenamento:** PostgreSQL (Modelagem Star Schema)
- **Analytics:** SQL Avançado (CTEs, Window Functions)
- **Orquestração:** Preparado para Apache Airflow / AWS Lambda

## 🩸 O Problema Resolvido
APIs financeiras falham e dados transacionais chegam sujos (nulos, tipagem incorreta). Este pipeline garante que:
1. Nenhuma transação seja duplicada caso o script rode duas vezes (Idempotência).
2. Quedas de rede sejam tratadas automaticamente sem derrubar o job.
3. Transações suspeitas (> R$ 10.000) sejam flaggadas na camada de transformação antes de chegarem ao Data Warehouse.

## 🚀 Como Executar
1. Clone o repositório.
2. Instale as dependências: `pip install pandas sqlalchemy requests`
3. Execute o motor de extração: `python etl_pipeline.py`
4. Rode as queries analíticas no banco via `analytics_fraud_detection.sql`
