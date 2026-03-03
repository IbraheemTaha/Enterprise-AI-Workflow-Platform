# Deployment & Verification Guide

**Version:** 1.1.0
**Last Updated:** March 3, 2026

---

## Overview

This guide covers how to deploy the Enterprise AI Workflow Platform, verify that all services are running correctly, and troubleshoot common issues. It is intended for developers setting up the platform on a new machine or after pulling the latest changes.

---

## System Requirements

| Component | Minimum Version | Command to Check |
|-----------|----------------|------------------|
| **Docker** | 24.0+ | `docker --version` |
| **Docker Compose** | 2.20+ | `docker compose version` |
| **Git** | 2.30+ | `git --version` |
| **Available RAM** | 16 GB recommended | — |
| **Available Disk** | 10 GB minimum | `df -h` |

### Required Ports (Must be Available)

All ports are configurable via `.env`. Default values:

```bash
lsof -i :8000  # FastAPI
lsof -i :8001  # LangChain
lsof -i :8002  # dbt docs
lsof -i :8080  # Airflow
lsof -i :8081  # Weaviate
lsof -i :8501  # Streamlit
lsof -i :5000  # MLflow
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :9000  # MinIO S3
lsof -i :9001  # MinIO Console
lsof -i :9090  # Prometheus
lsof -i :3000  # Grafana
lsof -i :7860  # Gradio
```

If any port is in use, update the corresponding variable in `.env` before starting.

---

## Step 1: Initial Setup

```bash
# Clone or update the repository
git clone <repo-url>
cd dev_RAG_with_Ananase

# Create .env from template and add your API keys
make setup
nano .env
```

**Required `.env` variables:**

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change_me_please
REDIS_PASSWORD=redispassword
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
AIRFLOW_FERNET_KEY=<generate with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())">
AIRFLOW_SECRET_KEY=<random string>

# At least one LLM key required; OpenAI or Google needed for RAG embeddings
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
```

---

## Step 2: Build and Start All Services

```bash
# Build and start all 16 services
make start

# Monitor startup progress
make logs
```

First startup takes several minutes due to image builds and dependency downloads.

---

## Step 3: Verify All Services Are Running

```bash
make ps
```

All services should show `Up` or `Up (healthy)`:

```
NAME                       STATUS
fastapi-api                Up (healthy)
langchain-service          Up (healthy)
streamlit-ui               Up (healthy)
gradio-ui                  Up
dbt-transform              Up
airflow-api-server         Up (healthy)
airflow-scheduler          Up
airflow-triggerer          Up
mlflow                     Up
postgres                   Up (healthy)
redis                      Up (healthy)
weaviate                   Up
minio                      Up
prometheus                 Up
grafana                    Up
```

Run automated health checks:

```bash
make health
```

---

## Step 4: Verify dbt Setup

### Test Database Connection

```bash
docker compose exec dbt bash
dbt debug
# Expected: Connection test: [OK connection ok]
exit
```

### Run dbt Models

```bash
docker exec dbt-transform dbt run

# Expected:
# Done. PASS=10 WARN=0 ERROR=0 SKIP=0 TOTAL=10
```

The 10 models:
- `dbt_staging`: `stg_categories`, `stg_customers`, `stg_employees`, `stg_order_details`, `stg_orders`, `stg_products`
- `dbt_marts`: `customer_analytics`, `employee_performance`, `product_performance`, `sales_summary`

### Run dbt Tests

```bash
docker exec dbt-transform dbt test
# Expected: Done. PASS=51 WARN=0 ERROR=0 SKIP=0 TOTAL=51
```

> **Note:** dbt models require the Northwind source data to be loaded first. Use the 3-step wizard in Streamlit → **DBT Platform** → **Northwind Demo** tab to load data and run dbt automatically.

### Verify Mart Tables in PostgreSQL

```bash
docker compose exec postgres psql -U postgres -d dbt_db

\dt dbt_marts.*
-- Should list: customer_analytics, employee_performance, product_performance, sales_summary

SELECT COUNT(*) FROM dbt_marts.sales_summary;      -- 830 rows
SELECT COUNT(*) FROM dbt_marts.customer_analytics;  -- 91 rows
SELECT COUNT(*) FROM dbt_marts.product_performance; -- 77 rows
SELECT COUNT(*) FROM dbt_marts.employee_performance; -- 9 rows

\q
```

---

## Step 5: Test Streamlit UI

1. Open **http://localhost:8501**
2. Verify the Home page loads
3. Navigate to each page using the sidebar:

### Chat Page
- Select a provider and model
- Send a test message
- Verify a response is returned

### System Health Page
- All service cards should display a health status
- Quick links to external UIs are visible

### LangChain Demo Page
- **Chat Chain tab**: send a message and verify a response
- **Document Ingestion tab**: ingest a test document
- **RAG Query tab**: query the ingested document
- **Documentation tab**: LangChain README renders

### DBT Platform Page

**First-time setup — run the 3-step wizard:**
1. Navigate to **Northwind Demo** tab
2. Click **🚀 Start Demo Setup**
3. **Step 1 — Load Dataset**: click **▶️ Load Dataset**, wait for all row counts in the log, then click **▶️ Next Step →**
4. **Step 2 — Run DBT Transformation**: click **▶️ Run DBT Transformation**, wait for `PASS=10` in output, then click **▶️ Next Step →**
5. **Step 3 — Verify Tables**: click **▶️ Verify Tables**, confirm "🎉 Northwind Demo is Ready!", then click **🚀 Start Exploring Analytics**

**After wizard completes:**
- [ ] **Dashboard** tab: KPI metrics load (830 orders, ~$1.27M revenue), charts display
- [ ] **Data Explorer** tab: table selector works, data displays
- [ ] **SQL Query** tab: sample queries execute, results display
- [ ] **Analytics** tab: product and employee performance charts render

**Reset Demo (optional):**
- The **🗑️ Reset Demo** expander (top-right of Northwind Demo tab) drops all data and schemas so the wizard can be re-run

### FastAPI Docs Page
- **Overview tab**: endpoint descriptions and curl examples display
- **API Explorer tab**: execute `/health`, `/v1/models`, and a chat completion
- **Provider Guide tab**: provider cards expand correctly

---

## Step 6: Troubleshooting

### Issue 1: Streamlit "Connection Closed" Error

**Symptom:**
```
OperationalError: server closed the connection unexpectedly
```

**Fix:**
```bash
docker compose up -d --force-recreate streamlit
```

**Root Cause:** Database connection closed between requests. Connections are opened fresh per query (no persistent pool).

---

### Issue 2: dbt Models Not Found

**Symptom:**
```
Relation dbt_staging.stg_orders not found
```

**Root Cause:** Northwind source tables have not been loaded into PostgreSQL.

**Fix:** Use the Streamlit wizard to load data first:
1. Open **DBT Platform** → **Northwind Demo** tab
2. Use **🗑️ Reset Demo** if partial data exists
3. Run all 3 wizard steps (Load → DBT → Verify)

Or verify source tables manually:
```bash
docker exec postgres psql -U postgres -d dbt_db -c "\dt public.*" | grep customers
```

---

### Issue 3: Port Already in Use

**Symptom:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8501: bind: address already in use
```

**Fix:**
```bash
# Kill the process using the port
lsof -ti :8501 | xargs kill -9

# Or change the port in .env:
# STREAMLIT_PORT=8502
```

---

### Issue 4: LLM API Not Responding

**Symptom:** Chat returns an error about provider configuration.

**Fix:**
1. Check that the API key is set in `.env`
2. Verify the key is active at the provider's console
3. Run `make restart` to apply `.env` changes

```bash
curl http://localhost:8000/health
# Should show which providers are configured
```

---

### Issue 5: Airflow Not Starting

**Symptom:** Airflow UI returns a 503 error.

**Fix:**
```bash
docker compose logs airflow-api-server | tail -50
docker compose restart airflow-api-server airflow-scheduler airflow-triggerer
```

Airflow requires that the `airflow_db` database is initialized first. The `airflow-init` service handles this on first startup.

---

## Step 7: Data Validation

### Validate Mart Row Counts

```sql
-- Connect to database
docker compose exec postgres psql -U postgres -d dbt_db

-- Validate all marts
SELECT
    'sales_summary'       AS table_name, COUNT(*) AS row_count FROM dbt_marts.sales_summary
UNION ALL
SELECT
    'product_performance', COUNT(*) FROM dbt_marts.product_performance
UNION ALL
SELECT
    'employee_performance', COUNT(*) FROM dbt_marts.employee_performance
UNION ALL
SELECT
    'customer_analytics',  COUNT(*) FROM dbt_marts.customer_analytics;

-- Expected:
-- sales_summary:          830
-- product_performance:    77
-- employee_performance:   9
-- customer_analytics:     91
```

### Revenue Sanity Check

```sql
SELECT SUM(net_revenue)::NUMERIC(12,2) FROM dbt_marts.sales_summary;
-- Expected: ~1,270,000.00
```

---

## Step 8: Final System Health Check

```bash
#!/bin/bash
# scripts/check_system_health.sh

echo "=== System Health Check ==="

echo "Checking Docker containers..."
docker compose ps | grep -q "Up" && echo "  ✅ Containers running" || echo "  ❌ Containers not running"

echo "Checking Streamlit..."
curl -s http://localhost:8501/healthz | grep -q "ok" && echo "  ✅ Streamlit healthy" || echo "  ❌ Streamlit not responding"

echo "Checking FastAPI..."
curl -s http://localhost:8000/health > /dev/null && echo "  ✅ FastAPI healthy" || echo "  ❌ FastAPI not responding"

echo "Checking LangChain..."
curl -s http://localhost:8001/health > /dev/null && echo "  ✅ LangChain healthy" || echo "  ❌ LangChain not responding"

echo "Checking PostgreSQL..."
docker compose exec -T postgres psql -U postgres -d dbt_db -c "SELECT 1;" &>/dev/null && echo "  ✅ Database connected" || echo "  ❌ Database not accessible"

echo "Checking dbt mart tables..."
COUNT=$(docker compose exec -T postgres psql -U postgres -d dbt_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='dbt_marts';" | tr -d ' ')
[ "$COUNT" -eq 4 ] && echo "  ✅ All 4 mart tables exist" || echo "  ⚠️  Expected 4 mart tables, found: $COUNT"

echo "=== Health Check Complete ==="
```

Run with:
```bash
chmod +x scripts/check_system_health.sh
./scripts/check_system_health.sh
```

---

## Release Readiness Checklist

### Functionality
- [ ] All services start successfully (`make ps`)
- [ ] Automated health checks pass (`make health`)
- [ ] Streamlit pages load without errors (all 5 pages)
- [ ] Northwind demo wizard completes all 3 steps
- [ ] dbt tests pass (51/51)
- [ ] LLM chat works for at least one configured provider
- [ ] RAG ingestion and query work (requires OpenAI or Google key)

### Security
- [ ] All default passwords changed in `.env`
- [ ] `.env` is not committed to version control (verify `.gitignore`)
- [ ] API keys are not hardcoded in any source file
- [ ] Exposed ports reviewed — only necessary ports accessible externally

### Documentation
- [ ] README.md is up to date
- [ ] All service URLs and ports correct in documentation
- [ ] Environment variable documentation complete

---

## Additional Resources

- **Main README**: [README.md](../README.md)
- **Quick Start**: [docs/QUICKSTART.md](QUICKSTART.md)
- **Architecture**: [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- **Northwind Demo**: [services/streamlit/NORTHWIND_DEMO.md](../services/streamlit/NORTHWIND_DEMO.md)
- **LangChain README**: [services/streamlit/LANGCHAIN_README.md](../services/streamlit/LANGCHAIN_README.md)

---

*Review and update this document with each major release.*
