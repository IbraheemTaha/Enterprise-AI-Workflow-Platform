# Quick Start Guide

## Prerequisites
- Docker 24.0+
- Docker Compose 2.20+
- 16GB RAM minimum

## Setup Steps

1. **Configure Environment**
   ```bash
   make setup   # Creates .env from .env.example
   nano .env    # Add your API keys
   ```

2. **Start Services**
   ```bash
   make start
   ```

3. **Access Services**
   - **Gradio UI**: http://localhost:7860 (simple chat interface)
   - **Streamlit UI**: http://localhost:8501 (advanced interface with demos)
   - **API Docs**: http://localhost:8000/docs
   - **LangChain API**: http://localhost:8001/docs
   - **dbt Docs**: http://localhost:8002 (data transformation lineage)
   - **Airflow**: http://localhost:8080 (admin/admin)
   - **MLflow**: http://localhost:5000
   - **Grafana**: http://localhost:3000 (admin/admin)

## First Steps

### 1. Test the API
```bash
curl http://localhost:8000/health
```

### 2. Open Gradio UI
Navigate to http://localhost:7860 and start chatting!

### 3. Explore Streamlit UI
Navigate to http://localhost:8501 for:
- Multi-provider chat interface
- System health dashboard
- LangChain demo playground
- Analytics and metrics

### 4. Try LangChain RAG
Ingest a document:
```bash
curl -X POST http://localhost:8001/ingest \
  -H "Content-Type: application/json" \
  -d '{"text": "LangChain is a framework for building LLM applications.", "metadata": {"source": "test"}}'
```

Query with RAG:
```bash
curl -X POST http://localhost:8001/rag/dynamic \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai", "query": "What is LangChain?"}'
```

### 5. Explore dbt
Navigate to http://localhost:8002 to view:
- Data lineage graph (DAG)
- Model documentation
- Column-level descriptions
- Test results

Run dbt commands:
```bash
docker compose exec dbt dbt run
docker compose exec dbt dbt test
```

### 6. Check Airflow
- Go to http://localhost:8080
- Login with admin/admin
- See your DAGs running

## Troubleshooting

**Services won't start?**
```bash
docker compose logs
```

**Out of memory?**
- Increase Docker memory limit to 16GB

**Port already in use?**
- Change the corresponding port variable in `.env` and restart services
