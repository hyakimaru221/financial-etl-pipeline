# 🚀 Financial Data Pipeline: ETL & Fraud Detection

## 👁️ Architecture Overview
A production-grade Data Engineering pipeline built to extract, sanitize, and model financial transactions. The core architecture is strictly focused on **Absolute Idempotency (Batch UPSERTs)**, **Network Resilience (Exponential Backoff)**, and **Velocity-Based Fraud Heuristics**.

## ⚙️ Tech Stack
- **Extraction & Transformation:** Python (Pandas, Requests)
- **Storage & Analytics:** PostgreSQL (Advanced SQL, CTEs, Window Functions, Performance Indexing)
- **Infrastructure:** Docker & Docker Compose (Fully Containerized)

## 🩸 Business Value & Problem Statement
Financial APIs fail, and transactional data often arrives dirty. This pipeline guarantees:
1. **Zero Duplication:** Strict idempotency using PostgreSQL `ON CONFLICT DO UPDATE` (Batch UPSERT) to prevent data duplication even under concurrent executions.
2. **Fault Tolerance:** Network drops are handled automatically via Exponential Backoff without crashing the main job.
3. **Advanced Fraud Heuristics:** Flags suspicious transactions based on volume (> $10,000) AND velocity (e.g., > 3 transactions in a 10-minute window) using optimized SQL Window Functions.

## 🚀 Deployment (Dockerized)
The infrastructure is fully containerized for zero-friction deployment.

1. Clone the repository.
2. Spin up the ETL pipeline and the PostgreSQL Data Warehouse:
   ```bash
   docker-compose up -d --build
   ```
3. The pipeline will automatically extract, sanitize, and load the data into the database.
