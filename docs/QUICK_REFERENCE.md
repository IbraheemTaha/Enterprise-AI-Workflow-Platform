# Quick Reference

**Version:** 1.1.0 | **Last Updated:** March 3, 2026

---

## Setup (5 minutes)

```bash
# First-time setup
make setup          # Create .env from template
nano .env           # Add API keys and passwords
make start          # Build and start all 16 services

# After pulling changes
docker compose build --no-cache streamlit   # Rebuild affected service
make start
```

---

## Health Check (2 minutes)

```bash
./scripts/check_system_health.sh
```

Or manually:

```bash
make ps             # View service status
make health         # Run automated checks
make logs           # Follow logs
```

---

## Verify the UI (5 minutes)

Open: **http://localhost:8501**

| Page | What to Verify |
|------|---------------|
| Home | Loads, all nav links visible |
| Chat | Select provider + model, send a message, get a response |
| System Health | Service status cards appear |
| LangChain Demo | Chat and RAG tabs respond; docs tab renders |
| DBT Platform | Run 3-step Northwind wizard; dashboard charts load |
| FastAPI Docs | API Explorer executes `/health` successfully |

**Northwind Demo wizard:**
1. DBT Platform → **Northwind Demo** tab → **🚀 Start Demo Setup**
2. Step 1: **▶️ Load Dataset** — wait for row counts in log → **▶️ Next Step**
3. Step 2: **▶️ Run DBT Transformation** — wait for `PASS=10` → **▶️ Next Step**
4. Step 3: **▶️ Verify Tables** — confirm "🎉 Northwind Demo is Ready!"

---

## Verify dbt (2 minutes)

```bash
# Run all 10 models
docker exec dbt-transform dbt run
# Expected: Done. PASS=10 WARN=0 ERROR=0 SKIP=0 TOTAL=10

# Run 51 data quality tests
docker exec dbt-transform dbt test
# Expected: Done. PASS=51 WARN=0 ERROR=0 SKIP=0 TOTAL=51
```

---

## Verify Database (1 minute)

```bash
docker compose exec postgres psql -U postgres -d dbt_db

SELECT SUM(total_orders) FROM dbt_marts.sales_summary;  -- 830
SELECT COUNT(*)          FROM dbt_marts.customer_analytics;  -- 91

\q
```

---

## Service URLs (default ports)

| Service | URL | Login |
|---------|-----|-------|
| Streamlit UI | http://localhost:8501 | — |
| Gradio UI | http://localhost:7860 | — |
| FastAPI Docs | http://localhost:8000/docs | — |
| LangChain Docs | http://localhost:8001/docs | — |
| dbt Docs | http://localhost:8002 | — |
| Airflow | http://localhost:8080 | admin / admin |
| MLflow | http://localhost:5000 | — |
| Grafana | http://localhost:3000 | admin / admin |
| Prometheus | http://localhost:9090 | — |
| MinIO Console | http://localhost:9001 | minioadmin / minioadmin123 |
| Weaviate | http://localhost:8081 | — |

All ports are configurable via `.env`.

---

## Common Issues & Fixes

### "Connection Closed" Error in Streamlit
```bash
docker compose up -d --force-recreate streamlit
```

### dbt Models Not Found
Source tables not loaded. Use the **Northwind Demo wizard** in Streamlit to load data first, or reset and re-run:
```bash
# Verify source tables
docker exec postgres psql -U postgres -d dbt_db -c "\dt public.*" | grep customers
```

### Port Already in Use
```bash
lsof -ti :8501 | xargs kill -9
# Or update the port in .env and restart
```

### LLM Not Responding
```bash
curl http://localhost:8000/health
# Check which providers show as configured
```

### Airflow Not Starting
```bash
docker compose logs airflow-api-server | tail -50
docker compose restart airflow-api-server airflow-scheduler
```

---

## Before Public Release

- [ ] All service health checks pass
- [ ] Northwind demo wizard works end-to-end
- [ ] dbt tests pass (51/51)
- [ ] LLM chat works with at least one provider
- [ ] RAG query works (requires OpenAI or Google key)
- [ ] `.env` not committed to git
- [ ] Default passwords changed
- [ ] Port exposure reviewed

---

## Documentation

| Document | Purpose |
|----------|---------|
| [README.md](../README.md) | Project overview and service descriptions |
| [docs/QUICKSTART.md](QUICKSTART.md) | Step-by-step getting started guide |
| [docs/ARCHITECTURE.md](ARCHITECTURE.md) | System architecture and data flow |
| [docs/DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Full deployment and verification guide |
| [services/streamlit/NORTHWIND_DEMO.md](../services/streamlit/NORTHWIND_DEMO.md) | Northwind demo walkthrough |
| [services/streamlit/LANGCHAIN_README.md](../services/streamlit/LANGCHAIN_README.md) | LangChain API reference |
