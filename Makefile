-include .env
export

.PHONY: help setup start stop logs clean test restart ps health

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

start:
	docker compose up -d
	@echo "✅ Services started!"
	@echo "Access:"
	@echo "  - Gradio UI: http://localhost:7860"
	@echo "  - API: http://localhost:8000/docs"
	@echo "  - Airflow: http://localhost:8080"
	@echo "  - MLflow: http://localhost:5000"
	@echo "  - Grafana: http://localhost:3000"

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
	@curl -sf http://localhost:8000/health && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 Airflow API Server"
	@curl -sf http://localhost:8080/api/v2/version && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 MLflow"
	@curl -sf http://localhost:5000 && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 Weaviate"
	@curl -sf http://localhost:8081/v1/.well-known/ready && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 MinIO API"
	@curl -sf http://localhost:9000/minio/health/ready && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 MinIO Console"
	@curl -sf http://localhost:9001 && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 Prometheus"
	@curl -sf http://localhost:9090/-/healthy && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 Grafana"
	@curl -sf http://localhost:3000/api/health && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 PostgreSQL"
	@docker compose exec -T postgres pg_isready -U $(POSTGRES_USER) >/dev/null 2>&1 && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "🟢 Redis"
	@docker compose exec -T redis redis-cli -a $(REDIS_PASSWORD) ping | grep -q PONG && echo " ✅ OK" || echo " ❌ FAILED"
	@echo ""

	@echo "✅ Health check completed."