# Architecture Overview

## System Components

### 1. API Layer
- **FastAPI** - Main REST API for LLM inference
- **LangChain** - Chain/RAG/Agent orchestration service
- **Gradio** - Simple web UI for quick interactions
- **Streamlit** - Advanced web UI with analytics and demos

### 2. ML Operations & Data Transformation
- **Airflow** - Workflow orchestration
- **MLflow** - Experiment tracking
- **dbt** - Data transformation and testing

### 3. Data Layer
- **PostgreSQL** - Metadata storage (shared by Airflow, MLflow, API, and LangChain)
- **Redis** - Caching (API uses db/0, LangChain uses db/1)
- **Weaviate** - Vector database for RAG
- **MinIO** - Object storage

### 4. Monitoring
- **Prometheus** - Metrics collection
- **Grafana** - Visualization

## Data Flow

1. User → Gradio UI / Streamlit UI / API
2. Streamlit → FastAPI (port 8000) / LangChain (port 8001)
3. API → LLM Providers (OpenAI/Anthropic/Gemini/Amazon Nova)
4. LangChain → Chains → LLM Providers
5. LangChain → RAG → Weaviate (vector search)
6. LangChain → Redis (response caching)
7. LangChain → PostgreSQL (conversation history)
9. Airflow → Scheduled ML tasks
10. MLflow → Available for experiment tracking and artifact storage (user-integrated)
11. dbt → Transform data in PostgreSQL
12. dbt → Generate documentation and lineage
13. Prometheus → Collect metrics
14. Grafana → Visualize data

## LangChain Service

The LangChain service provides three main capabilities:

### 1. Chat Chains
- Multi-provider LLM access (OpenAI, Anthropic, Google, AWS)
- Conversation memory stored in PostgreSQL
- Response caching via Redis

### 2. RAG (Retrieval Augmented Generation)
- Document ingestion into Weaviate vector store
- Vector search for relevant context
- Context-aware responses with source citations

### 3. Agents
- Tool-using agents with ReAct reasoning (not yet implemented)

### Integration Points
- **PostgreSQL**: Conversation history (langchain database)
- **Redis**: Response and embedding caching (db/1)
- **Weaviate**: Vector storage for RAG
- **MLflow**: Chain performance tracking
- **All LLM Providers**: OpenAI, Anthropic, Google, AWS Bedrock

## dbt Service

The dbt service provides SQL-based data transformation capabilities:

### Features
- **SQL Transformations**: Transform data using SQL and Jinja templating
- **Data Testing**: Built-in and custom data quality tests
- **Documentation**: Auto-generated data lineage and documentation
- **Incremental Models**: Efficient processing of large datasets

### Integration Points
- **PostgreSQL**: Connects to `dbt_db` database, creates `dbt_staging` and `dbt_marts` schemas
- **Documentation Server**: Serves interactive docs on port 8002
- **Version Control**: All transformations tracked in code
