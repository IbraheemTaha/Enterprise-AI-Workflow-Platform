# 🚀 Enterprise AI Workflow Platform

A local, Docker Compose based AI and MLOps platform that combines workflow orchestration, experiment tracking, APIs, storage, monitoring, and UI components into a single reproducible environment.

This repository focuses on **infrastructure and integration**, not on a finished AI product.

---

## 🧩 What This Project Provides

This platform runs the following components:

- **FastAPI** (API layer)
- **Gradio** (simple UI for the API)
- **Apache Airflow 3.1.6** (workflow orchestration)
- **MLflow** (experiment tracking and artifacts)
- **PostgreSQL 18.1** (shared relational database for Airflow, MLflow, and API data)
- **Redis 8.4** (cache / fast key-value store)
- **Weaviate 1.34.8** (vector database, empty by default)
- **MinIO** (S3-compatible object storage)
- **Prometheus** (metrics collection)
- **Grafana** (metrics visualization)

All services run on a single Docker bridge network and can be managed using the provided Makefile.

---

## 🔧 Technology Stack

| Component | Version | Purpose |
|-----------|---------|---------|
| Python | 3.12 | Runtime |
| Apache Airflow | 3.1.6 | Workflow orchestration |
| MLflow | latest | Experiment tracking |
| FastAPI | latest | API service |
| Gradio | latest | Web UI |
| PostgreSQL | 18.1 | Relational database |
| Redis | 8.4 | In-memory store |
| Weaviate | 1.34.8 | Vector database |
| MinIO | latest | Object storage |
| Prometheus | latest | Metrics |
| Grafana | latest | Dashboards |
| Docker | 24.0+ | Containerization |

---

## 📋 Prerequisites

- Docker Desktop 24.0+
- Docker Compose 2.20+
- 16 GB RAM recommended
- Enough disk space for Docker images and volumes

**Supported systems:**
- macOS
- Linux
- Windows (with WSL2)

---

## 📁 Project Structure

```
.
├── docker-compose.yml
├── Makefile
├── .env
├── services/
│   ├── api/          # FastAPI service
│   ├── airflow/      # Custom Airflow image + DAGs
│   ├── gradio/       # Gradio UI
│   └── mlflow/       # MLflow image
└── scripts/
    └── init-databases.sh
```

---

## ⚙️ Environment Configuration

- Running `make setup` will automatically create `.env` from `.env.example` if it doesn't exist.
- Edit `.env` before starting to customize passwords and add API keys.


**Minimum required variables:**

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change_me_please
POSTGRES_DB=postgres

REDIS_PASSWORD=redispassword

MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123

AIRFLOW_FERNET_KEY=your_fernet_key
AIRFLOW_SECRET_KEY=your_secret_key
AIRFLOW_UID=1000
```

**Optional API keys** (used by the API container and Airflow tasks only):

```env
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_API_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_REGION=us-east-1
```

---

## 🚀 Quick Start

```bash
make setup    # Checks Docker, creates .env from .env.example
make start    # Start all services
```

This runs:

```bash
docker compose up -d
```

First startup may take a few minutes due to image builds and downloads.

---

## ✅ Verify

```bash
make ps
make health
```

---

## 📌 Service Access

| Service | URL | Notes |
|---------|-----|-------|
| Gradio UI | http://localhost:7860 | Frontend |
| FastAPI Docs | http://localhost:8000/docs | API docs |
| Airflow | http://localhost:8080 | admin / admin |
| MLflow | http://localhost:5000 | Tracking UI |
| Weaviate | http://localhost:8081 | Vector DB |
| MinIO API | http://localhost:9000 | S3 endpoint |
| MinIO Console | http://localhost:9001 | Web UI |
| Prometheus | http://localhost:9090 | Metrics |
| Grafana | http://localhost:3000 | admin / admin |

---

## 🛠 Commands

```bash
make setup      # Check prerequisites and create .env from .env.example
make start      # Start all services
make stop       # Stop all services
make restart    # Restart all services
make ps         # Show service status
make logs       # Follow logs
make health     # Run health checks
make clean      # Stop and delete volumes
```

---

## ❤️ Health Checks

Run:

```bash
make health
```

It checks:

- **FastAPI:** `http://localhost:8000/health`
- **Airflow API:** `http://localhost:8080/api/v2/version`
- **MLflow:** `http://localhost:5000`
- **Weaviate readiness:** `http://localhost:8081/v1/.well-known/ready`
- **MinIO readiness:** `http://localhost:9000/minio/health/ready`
- **Prometheus:** `http://localhost:9090/-/healthy`
- **Grafana:** `http://localhost:3000/api/health`
- **PostgreSQL readiness** via `pg_isready` (inside container)
- **Redis connectivity** via `AUTH` + `PING` (inside container)

---

## 🔌 API Behavior (Current)

The FastAPI service currently exposes:

- `GET /`
- `GET /health`
- `POST /v1/chat/completions` (placeholder response)

**Example:**

```bash
curl http://localhost:8000/health
```

No LLM calls or RAG logic are implemented yet.

---

## 🔄 Airflow

- Database migration runs via `airflow-init`
- Airflow API server, scheduler, and triggerer run as separate containers
- DAGs live in:

```
services/airflow/dags/
```

Any DAG placed there appears automatically in Airflow.

---

## 📊 Monitoring

- **Prometheus** is available at http://localhost:9090
- **Grafana** is available at http://localhost:3000
- Dashboards are not preconfigured yet (you can add them later)

---

## 🔐 Security Notes

This setup is for **local development only**.

Before production use:

- Change all default passwords
- Add authentication to FastAPI
- Restrict exposed ports
- Use HTTPS
- Store secrets securely (do not commit `.env`)

---

## 📄 License

MIT

---

## 📦 Changelog

### 1.0.1 – February 2026
- Added `setup` command in the Makefile that checks prerequisites and creates `.env` from `.env.example`
- Deleted `setup.sh` file
- Imperoved `scripts/init-databases.sh` file adding the `AirFlow` database
- Clarified `PostgreSQL` multi-database usage
- Updated environment variable examples
- Improved documentation consistency

### 1.0.0 – January 2026
- Initial release



---
## ⭐ Star History

If you find this project useful, please consider giving it a star on GitHub!


**Built with ❤️ for the AI community**
