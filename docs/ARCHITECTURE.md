# Architecture Overview

## System Components

### 1. API Layer
- **FastAPI** - Main inference API
- **Gradio** - Web UI

### 2. ML Operations
- **Airflow** - Workflow orchestration
- **MLflow** - Experiment tracking

### 3. Data Layer
- **PostgreSQL** - Metadata storage
- **Redis** - Caching
- **Weaviate** - Vector database
- **MinIO** - Object storage

### 4. Monitoring
- **Prometheus** - Metrics collection
- **Grafana** - Visualization

## Data Flow

1. User → Gradio UI / API
2. API → LLM Providers (OpenAI/Anthropic/Gemini/Amazon Nova)
3. API → Vector DB (for RAG)
4. Airflow → Scheduled ML tasks
5. MLflow → Track experiments
6. Prometheus → Collect metrics
7. Grafana → Visualize data
