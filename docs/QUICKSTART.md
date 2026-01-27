# Quick Start Guide

## Prerequisites
- Docker 24.0+
- Docker Compose 2.20+
- 16GB RAM minimum

## Setup Steps

1. **Configure Environment**
   ```bash
   nano .env  # Add your API keys
   ```

2. **Start Services**
   ```bash
   make start
   ```

3. **Access Services**
   - Gradio UI: http://localhost:7860
   - API Docs: http://localhost:8000/docs
   - Airflow: http://localhost:8080 (admin/admin)
   - MLflow: http://localhost:5000
   - Grafana: http://localhost:3000 (admin/admin)

## First Steps

### 1. Test the API
```bash
curl http://localhost:8000/health
```

### 2. Open Gradio UI
Navigate to http://localhost:7860 and start chatting!

### 3. Check Airflow
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
- Change ports in docker-compose.yml
