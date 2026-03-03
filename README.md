# Enterprise AI Workflow Platform

A local, Docker Compose based AI and MLOps platform that combines workflow orchestration, experiment tracking, APIs, storage, monitoring, and UI components into a single reproducible environment.

This repository focuses on **infrastructure and integration**, not on a finished AI product.

---

## What This Project Provides

- **FastAPI** — multi-LLM API layer (OpenAI, Anthropic, Google Gemini, Amazon Bedrock)
- **Gradio** — simple web UI for the API
- **Streamlit** — advanced multi-page web UI with analytics
- **LangChain** — chain / RAG / agent orchestration service
- **dbt** — SQL data transformation and testing (Northwind demo included)
- **Apache Airflow 3.1.6** — workflow orchestration and DAG scheduling
- **MLflow** — experiment tracking and artifact storage
- **PostgreSQL 18.1** — shared relational database
- **Redis 8.4** — in-memory cache / key-value store
- **Weaviate 1.34.8** — vector database for RAG
- **MinIO** — S3-compatible object storage
- **Prometheus** — metrics collection
- **Grafana** — metrics visualization

All services run on a single Docker bridge network and are managed via the Makefile.

---

## Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12 | Runtime |
| Apache Airflow | 3.1.6 | Workflow orchestration |
| MLflow | 3.7.0 | Experiment tracking |
| FastAPI | 0.128.0 | API service |
| Gradio | 5.10.0 | Simple web UI |
| Streamlit | 1.54.0 | Advanced web UI |
| LangChain | 1.2.10 | Chain / RAG / Agent orchestration |
| dbt | 1.9 | Data transformation & testing |
| PostgreSQL | 18.1 | Relational database |
| Redis | 8.4 | In-memory store |
| Weaviate | 1.34.8 | Vector database |
| MinIO | latest | Object storage |
| Prometheus | latest | Metrics |
| Grafana | latest | Dashboards |
| Docker | 24.0+ | Containerization |

---

## Prerequisites

- Docker Desktop 24.0+
- Docker Compose 2.20+
- 16 GB RAM recommended

**Supported systems:** macOS, Linux, Windows (WSL2)

---

## Project Structure

```
.
├── docker-compose.yml
├── Makefile
├── .env
├── services/
│   ├── api/          # FastAPI backend service
│   ├── airflow/      # Custom Airflow image + DAGs
│   ├── gradio/       # Gradio web UI (simple interface)
│   ├── streamlit/    # Streamlit web UI (advanced interface)
│   ├── langchain/    # LangChain service (chains, RAG, agents)
│   ├── dbt/          # dbt data transformation models
│   └── mlflow/       # MLflow tracking server
└── scripts/
    └── init-databases.sh
```

---

## Environment Configuration

Running `make setup` creates `.env` from `.env.example` automatically. Edit it before starting.

**Required:**
```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change_me_please
POSTGRES_DB=postgres

REDIS_PASSWORD=redis123           # default from .env.example — change as needed

MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123

AIRFLOW_FERNET_KEY=your_fernet_key
AIRFLOW_SECRET_KEY=your_secret_key
AIRFLOW_UID=1000
```

**LLM API Keys** (at least one required; OpenAI or Google needed for RAG embeddings):
```env
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
```

**Ports** (all host ports are configurable to avoid conflicts):
```env
POSTGRES_PORT=5432
REDIS_PORT=6379
MINIO_API_PORT=9000
MINIO_CONSOLE_PORT=9001
WEAVIATE_PORT=8081
MLFLOW_PORT=5000
AIRFLOW_PORT=8080
FASTAPI_PORT=8000
GRADIO_PORT=7860
LANGCHAIN_PORT=8001
STREAMLIT_PORT=8501
DBT_PORT=8002
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

**Database names** (each service uses its own PostgreSQL database):
```env
MLFLOW_DB=mlflow_db
FASTAPI_DB=fastapi_db
AIRFLOW_DB=airflow_db
LANGCHAIN_DB=langchain_db
DBT_DB=dbt_db
```

---

## Quick Start

```bash
make setup    # Check Docker, create .env from .env.example
make start    # Build and start all services
```

First startup takes a few minutes due to image builds and downloads.

---

## Verify

```bash
make ps       # Show service status
make health   # Run health checks on all services
```

---

## Service Access

URLs use `${VAR:-default}` — the value from your `.env`, falling back to the default shown.

| Service | URL | `.env` variable |
|---------|-----|-----------------|
| Gradio UI | `http://localhost:${GRADIO_PORT:-7860}` | `GRADIO_PORT` |
| Streamlit UI | `http://localhost:${STREAMLIT_PORT:-8501}` | `STREAMLIT_PORT` |
| FastAPI Docs | `http://localhost:${FASTAPI_PORT:-8000}/docs` | `FASTAPI_PORT` |
| LangChain API | `http://localhost:${LANGCHAIN_PORT:-8001}/docs` | `LANGCHAIN_PORT` |
| dbt Docs | `http://localhost:${DBT_PORT:-8002}` | `DBT_PORT` |
| Airflow | `http://localhost:${AIRFLOW_PORT:-8080}` | `AIRFLOW_PORT` |
| MLflow | `http://localhost:${MLFLOW_PORT:-5000}` | `MLFLOW_PORT` |
| Weaviate | `http://localhost:${WEAVIATE_PORT:-8081}` | `WEAVIATE_PORT` |
| MinIO Console | `http://localhost:${MINIO_CONSOLE_PORT:-9001}` | `MINIO_CONSOLE_PORT` |
| MinIO S3 | `http://localhost:${MINIO_API_PORT:-9000}` | `MINIO_API_PORT` |
| Prometheus | `http://localhost:${PROMETHEUS_PORT:-9090}` | `PROMETHEUS_PORT` |
| Grafana | `http://localhost:${GRAFANA_PORT:-3000}` | `GRAFANA_PORT` |

---

## Commands

```bash
make setup      # Check prerequisites and create .env
make start      # Start all services
make stop       # Stop all services
make restart    # Restart all services
make ps         # Show service status
make logs       # Follow logs
make health     # Run health checks
make clean      # Stop and delete volumes
```

---

## Services

---

### FastAPI

Multi-provider LLM API layer. Routes chat completions to OpenAI, Anthropic, Google Gemini, or Amazon Bedrock.

**Connects to:** LLM providers (OpenAI, Anthropic, Google, AWS Bedrock) directly via their APIs. Called by Streamlit (Chat page) and Gradio for all LLM completions.

**Access:** `http://localhost:${FASTAPI_PORT:-8000}/docs`

**Key endpoints:**
- `GET /health` — provider configuration status
- `GET /v1/models?provider=<provider>` — list available models (queries provider API live)
- `POST /v1/chat/completions` — chat with any supported LLM

```bash
# Chat example
curl -X POST http://localhost:${FASTAPI_PORT:-8000}/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"provider": "anthropic", "model": "claude-sonnet-4-5-20250929",
       "messages": [{"role": "user", "content": "Hello!"}]}'

# List OpenAI models
curl "http://localhost:${FASTAPI_PORT:-8000}/v1/models?provider=openai"
```

> The `model` field is optional — a sensible default is used per provider.

---

### Gradio

Simple web UI for chatting with the FastAPI LLM layer. Supports dynamic provider and model selection.

**Connects to:** FastAPI (`:8000`) — sends all chat completions to the LLM gateway.

**Access:** `http://localhost:${GRADIO_PORT:-7860}` — open in browser, no setup needed.

---

### Streamlit

Advanced multi-page web UI. Includes multi-turn chat, system health dashboard, LangChain RAG demo, and dbt analytics dashboard.

**Connects to:** FastAPI (`:8000`) for LLM chat completions; LangChain (`:8001`) for RAG queries, document ingestion, and chain demos; PostgreSQL `dbt_db` for dbt mart analytics; triggers `dbt run` inside the `dbt-transform` container via the Docker socket.

**Access:** `http://localhost:${STREAMLIT_PORT:-8501}`

**Pages:**
| Page | Description |
|------|-------------|
| Home | Platform overview |
| Chat | Multi-turn LLM chat with provider/model selector |
| Health | Live service health dashboard |
| LangChain Demo | RAG queries, chat, document ingestion |
| DBT Platform | Interactive analytics on Northwind data |
| FastAPI Docs | Live API explorer and provider setup guide |

---

### LangChain

FastAPI-based service wrapping LangChain. Supports multi-provider chat, RAG via Weaviate, and document ingestion.

**Connects to:** Weaviate (`:8081`) as the vector store for RAG document storage and retrieval; LLM providers (OpenAI, Anthropic, Google, AWS) for completions and embeddings. PostgreSQL `langchain_db` and Redis are pre-configured for future use. Called by Streamlit (LangChain Demo page).

**Access:** `http://localhost:${LANGCHAIN_PORT:-8001}/docs`

**Key endpoints:**
- `POST /chat/dynamic` — chat with any provider/model, full conversation history
- `POST /rag/dynamic` — RAG query against Weaviate (requires ingested documents)
- `POST /ingest` — ingest text into Weaviate for RAG

```bash
# RAG chat example
curl -X POST http://localhost:${LANGCHAIN_PORT:-8001}/chat/dynamic \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai", "model": "gpt-4o-mini",
       "messages": [{"role": "user", "content": "Summarize the docs"}]}'
```

> RAG ingestion requires `OPENAI_API_KEY` or `GOOGLE_API_KEY` for embeddings.

---

### dbt

SQL transformation service using the Northwind demo dataset (91 customers, 830 orders, $1.3M revenue). Implements a 3-layer medallion pipeline: raw sources → 6 staging views → 4 mart tables.

**Connects to:** PostgreSQL `dbt_db` — reads source tables from the `public` schema, writes to `dbt_staging` (views) and `dbt_marts` (tables). Triggered from Streamlit via the Docker socket; mart tables are consumed by Streamlit dashboards.

**Access:** `http://localhost:${DBT_PORT:-8002}` (interactive lineage & model docs)

**Run commands:**
```bash
docker exec dbt-transform dbt run           # Build all 10 models
docker exec dbt-transform dbt test          # Run 51 data quality tests
docker exec dbt-transform dbt docs generate # Refresh documentation
docker exec dbt-transform dbt run --select customer_analytics  # Single model
```

**Mart tables available in `dbt_marts.*`:**
- `customer_analytics` — lifetime revenue, customer segments (High Value / Medium Value / Low Value)
- `sales_summary` — daily revenue, order counts, month-to-date and year-to-date running totals
- `product_performance` — total revenue, reorder metrics
- `employee_performance` — sales totals, order counts, late shipment rate

**Query example:**
```bash
docker exec postgres psql -U postgres -d dbt_db -c \
  "SELECT customer_segment, COUNT(*), SUM(lifetime_revenue)
   FROM dbt_marts.customer_analytics GROUP BY customer_segment;"
```

> Explore outputs visually via Streamlit → **DBT Platform** page. Full walkthrough in `services/streamlit/NORTHWIND_DEMO.md`.

---

### Airflow

Workflow orchestration. Runs an API server, scheduler, and triggerer as separate containers.

**Connects to:** PostgreSQL `airflow_db` for metadata and task state. Uses `LocalExecutor` (no external queue required).

**Access:** `http://localhost:${AIRFLOW_PORT:-8080}` — login: `admin` / `admin`

**Add DAGs:** drop `.py` files into `services/airflow/dags/` — they appear in the UI automatically.

```python
# Example: schedule a daily dbt run
from airflow.operators.bash import BashOperator

dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command='docker exec dbt-transform dbt run && dbt test'
)
```

---

### MLflow

Experiment tracking, metric logging, and artifact storage.

**Connects to:** PostgreSQL `mlflow_db` for run metadata and metrics; MinIO (S3-compatible) for artifact storage.

**Access:** `http://localhost:${MLFLOW_PORT:-5000}`

```python
import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
with mlflow.start_run():
    mlflow.log_param("lr", 0.01)
    mlflow.log_metric("accuracy", 0.95)
    mlflow.log_artifact("model.pkl")
```

---

### PostgreSQL

Shared relational database. Each service uses an isolated database.

**Connection:** `postgresql://postgres:${POSTGRES_PASSWORD}@localhost:${POSTGRES_PORT:-5432}/<db_name>`

| Database | Used by |
|----------|---------|
| `airflow_db` | Airflow metadata |
| `mlflow_db` | MLflow runs & metrics |
| `fastapi_db` | FastAPI (pre-configured, available for use) |
| `langchain_db` | LangChain (pre-configured, available for use) |
| `dbt_db` | dbt source data and marts |

---

### Redis

In-memory cache and key-value store. `REDIS_URL` is pre-configured for FastAPI (`db=0`) and LangChain (`db=1`), ready for caching and session storage. Airflow uses `LocalExecutor` and does not require Redis.

**Connection:** `redis://:${REDIS_PASSWORD}@localhost:${REDIS_PORT:-6379}`

```bash
docker exec redis redis-cli -a $REDIS_PASSWORD PING   # → PONG
```

---

### Weaviate

Vector database used by LangChain for RAG document storage and semantic search. Starts empty.

**Access:** `http://localhost:${WEAVIATE_PORT:-8081}`

```bash
# Check readiness
curl http://localhost:${WEAVIATE_PORT:-8081}/v1/.well-known/ready

# List collections
curl http://localhost:${WEAVIATE_PORT:-8081}/v1/schema
```

Documents are ingested via the LangChain `POST /ingest` endpoint.

---

### MinIO

S3-compatible object storage. Used by MLflow for artifact storage. Console available for bucket management.

**Console:** `http://localhost:${MINIO_CONSOLE_PORT:-9001}` — login: `minioadmin` / `minioadmin123`
**S3 endpoint:** `http://localhost:${MINIO_API_PORT:-9000}`

```bash
# Using AWS CLI
aws --endpoint-url http://localhost:${MINIO_API_PORT:-9000} s3 ls
```

---

### Prometheus

Collects metrics from running services.

**Access:** `http://localhost:${PROMETHEUS_PORT:-9090}`

Metrics scrape targets are configured in `config/prometheus.yml`.

---

### Grafana

Metrics visualization and dashboards. No dashboards are pre-configured — add your own using PostgreSQL or Prometheus as data sources.

**Access:** `http://localhost:${GRAFANA_PORT:-3000}` — login: `admin` / `admin`

**Quick data source setup:** Settings → Data Sources → Add PostgreSQL → host `postgres:5432`, database `dbt_db`.

---

## Security Notes

This setup is for **local development only**.

Before production use:
- Change all default passwords in `.env`
- Add authentication to FastAPI and LangChain
- Restrict exposed ports
- Use HTTPS
- Never commit `.env`

---

## License

MIT

---

## Changelog

### 1.1.0 – March 3, 2026

**New services**
- **LangChain** (`${LANGCHAIN_PORT:-8001}`) — multi-provider chat and RAG via Weaviate, document ingestion, dynamic provider/model selection
- **Streamlit** (`${STREAMLIT_PORT:-8501}`) — multi-page UI: chat, health dashboard, LangChain demo, dbt analytics, FastAPI explorer
- **dbt** (`${DBT_PORT:-8002}`) — Northwind analytics platform: 10 models, 51 data quality tests, Streamlit integration

**Infrastructure**
- All 14 host ports configurable via `.env`
- All 5 PostgreSQL database names configurable via `.env`
- `docker-compose.yml` expanded to 16 services; all ports use `${VAR:-default}` syntax
- Fixed PostgreSQL port mapping and `init-databases.sh` Alpine compatibility
- Fixed Streamlit `psycopg2` dependency and database authentication

**LLM / AI**
- FastAPI `/v1/chat/completions` routes to real provider APIs (replaced placeholder stub)
- New `GET /v1/models?provider=<provider>` — live model listing per API key
- Dynamic provider and model selection across Streamlit, Gradio, and LangChain UIs
- Multi-turn conversation history in Streamlit Chat

### 1.0.1 – February 2026
- Added `setup` Makefile command with prerequisite checks
- Improved `scripts/init-databases.sh` — added Airflow database
- Updated environment variable examples and documentation

### 1.0.0 – January 2026
- Initial release

---

If you find this project useful, please consider giving it a star on GitHub!

**Built with ❤️ for the AI community**
