-include .env
export

.PHONY: help setup build start stop logs clean test restart ps health

help:
	@echo "Enterprise AI Workflow Platform"
	@echo ""
	@echo "Commands:"
	@echo "  make start  - Start all services"
	@echo "  make stop   - Stop all services"
	@echo "  make logs   - View logs"
	@echo "  make clean  - Clean everything"
	@echo "  make test   - Run tests"

setup:
	@echo "🚀 Setting up Enterprise AI Workflow Platform..."
	@command -v docker > /dev/null 2>&1 || { echo "❌ Docker not found. Install from: https://docs.docker.com/get-docker/"; exit 1; }
	@command -v docker compose > /dev/null 2>&1 || { echo "❌ Docker Compose not found."; exit 1; }
	@if [ ! -f .env ]; then \
		if [ -f .env.example ]; then \
			cp .env.example .env; \
			echo "✅ .env created from .env.example"; \
			echo "⚠️  Make sure to edit .env and add your API keys!"; \
		else \
			echo "❌ .env and .env.example not found."; \
			exit 1; \
		fi; \
	else \
		echo "✅ .env file found"; \
	fi
	@mkdir -p services/airflow/{dags,logs,plugins}
	@mkdir -p data
	@echo "✅ Setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "1. Edit .env file: nano .env"
	@echo "2. Add your API keys (OpenAI, Anthropic, Google, or AWS)"
	@echo "3. Run: make start"

build:
	docker compose build --no-cache
	@echo "✅ Services built successfully!"

start:
	docker compose up -d
	@echo "✅ Services started!"
	@echo "Access:"
	@echo "  - Gradio UI: http://localhost:$(GRADIO_PORT)"
	@echo "  - Streamlit UI: http://localhost:$(STREAMLIT_PORT)"
	@echo "  - API: http://localhost:$(FASTAPI_PORT)/docs"
	@echo "  - LangChain API: http://localhost:$(LANGCHAIN_PORT)/docs"
	@echo "  - dbt Docs: http://localhost:$(DBT_PORT)"
	@echo "  - Airflow: http://localhost:$(AIRFLOW_PORT)"
	@echo "  - MLflow: http://localhost:$(MLFLOW_PORT)"
	@echo "  - Grafana: http://localhost:$(GRAFANA_PORT)"

restart:
	docker compose restart

stop:
	docker compose down

logs:
	docker compose logs -f

clean:
	docker compose down -v
	rm -rf data/*

test:
	docker compose exec api pytest tests/ -v

ps:
	docker compose ps


health:
	@echo "🔍 Checking service health..."
	@echo ""

	@echo "🟢 API (FastAPI)"
	@curl -sfo /dev/null http://localhost:$(FASTAPI_PORT)/health && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 LangChain Service"
	@curl -sfo /dev/null http://localhost:$(LANGCHAIN_PORT)/health && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 Streamlit UI"
	@curl -sfo /dev/null http://localhost:$(STREAMLIT_PORT)/_stcore/health && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 dbt Docs"
	@curl -sfo /dev/null http://localhost:$(DBT_PORT) && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 Airflow API Server"
	@curl -sfo /dev/null http://localhost:$(AIRFLOW_PORT)/api/v2/version && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 MLflow"
	@curl -sfo /dev/null http://localhost:$(MLFLOW_PORT) && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 Weaviate"
	@curl -sfo /dev/null http://localhost:$(WEAVIATE_PORT)/v1/.well-known/ready && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 MinIO API"
	@curl -sfo /dev/null http://localhost:$(MINIO_API_PORT)/minio/health/ready && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 MinIO Console"
	@curl -sfo /dev/null http://localhost:$(MINIO_CONSOLE_PORT) && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 Prometheus"
	@curl -sfo /dev/null http://localhost:$(PROMETHEUS_PORT)/-/healthy && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 Grafana"
	@curl -sfo /dev/null http://localhost:$(GRAFANA_PORT)/api/health && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 PostgreSQL"
	@docker compose exec -T postgres pg_isready -U $(POSTGRES_USER) >/dev/null 2>&1 && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 Redis"
	@docker compose exec -T redis redis-cli -a $(REDIS_PASSWORD) ping 2>/dev/null | grep -q PONG && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "✅ Health check completed."