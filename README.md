# 🚀 Financial Data Pipeline: ETL & Fraud Detection

## 👁️ Architecture Overview
A production-grade Data Engineering pipeline built to extract, sanitize, and model financial transactions in real-time. The core architecture is strictly focused on **Idempotency**, **Network Resilience (Exponential Backoff)**, and **Cloud Cost Optimization**.

## ⚙️ Tech Stack
- **Extraction & Transformation:** Python (Pandas, Requests)
- **Storage:** PostgreSQL (Star Schema Modeling)
- **Analytics:** Advanced SQL (CTEs, Window Functions)
- **Orchestration:** Ready for Apache Airflow / AWS Lambda deployment

## 🩸 Business Value & Problem Statement
Financial APIs fail, and transactional data often arrives dirty (nulls, type mismatches). This pipeline guarantees that:
1. **Zero Duplication:** Transactions are never duplicated even if the script runs concurrently (Strict Idempotency).
2. **Fault Tolerance:** Network drops are handled automatically without crashing the main job.
3. **Fraud Flagging:** Suspicious transactions (> $10,000) are flagged at the transformation layer before reaching the Data Warehouse.

## 🚀 Deployment & Local Setup
1. Clone the repository.
2. Install dependencies:
   `pip install pandas sqlalchemy requests`
3. Run the ETL job:
   `python etl_pipeline.py`
