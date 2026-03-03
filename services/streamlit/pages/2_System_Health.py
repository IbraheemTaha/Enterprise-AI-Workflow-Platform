import streamlit as st
from utils.api_client import check_service_health, check_tcp_health, get_service_info
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os

# Page configuration
st.set_page_config(
    page_title="System Health - Enterprise AI Platform",
    page_icon="💚",
    layout="wide"
)

st.title("💚 System Health Dashboard")
st.markdown("Real-time monitoring of all platform services")

# Navigation
st.sidebar.title("Navigation")
st.sidebar.page_link("Home.py", label="🏠 Home")
st.sidebar.page_link("pages/1_Chat.py", label="📝 Chat")
st.sidebar.page_link("pages/2_System_Health.py", label="💚 System Health")
st.sidebar.page_link("pages/3_LangChain_Demo.py", label="🔗 LangChain Demo")
st.sidebar.page_link("pages/4_DBT_Platform.py", label="📊 DBT Platform")
st.sidebar.page_link("pages/5_FastAPI_Docs.py", label="⚡ FastAPI Docs")
st.sidebar.divider()

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)

# Refresh button
if st.sidebar.button("🔄 Refresh Now") or auto_refresh:
    st.rerun()

# ---------------------------------------------------------------------------
# HTTP services: (internal_url, external_url, health_path)
# ---------------------------------------------------------------------------
http_services = {
    "FastAPI":    ("http://api:8000",              f"http://localhost:{os.getenv('FASTAPI_PORT', '8000')}",    "/health"),
    "LangChain":  ("http://langchain:8001",         f"http://localhost:{os.getenv('LANGCHAIN_PORT', '8001')}",  "/health"),
    "Airflow":    ("http://airflow-api-server:8080", f"http://localhost:{os.getenv('AIRFLOW_PORT', '8080')}",   "/api/v2/version"),
    "MLflow":     ("http://mlflow:5000",             f"http://localhost:{os.getenv('MLFLOW_PORT', '5000')}",    "/health"),
    "Weaviate":   ("http://weaviate:8080",           f"http://localhost:{os.getenv('WEAVIATE_PORT', '8081')}",  "/v1/.well-known/ready"),
    "Prometheus": ("http://prometheus:9090",         f"http://localhost:{os.getenv('PROMETHEUS_PORT', '9090')}", "/-/healthy"),
    "Grafana":    ("http://grafana:3000",            f"http://localhost:{os.getenv('GRAFANA_PORT', '3000')}",   "/api/health"),
    "MinIO":      ("http://minio:9000",              f"http://localhost:{os.getenv('MINIO_API_PORT', '9000')}", "/minio/health/live"),
    "Gradio":     ("http://gradio:7860",             f"http://localhost:{os.getenv('GRADIO_PORT', '7860')}",    "/"),
    "dbt":        ("http://dbt:8002",                f"http://localhost:{os.getenv('DBT_PORT', '8002')}",       "/"),
}

# ---------------------------------------------------------------------------
# TCP services: (internal_host, internal_port, external_port)
# ---------------------------------------------------------------------------
tcp_services = {
    "PostgreSQL": ("postgres", 5432, os.getenv("POSTGRES_PORT", "5432")),
    "Redis":      ("redis",    6379, os.getenv("REDIS_PORT",    "6379")),
}

# ---------------------------------------------------------------------------
# Render a single service card (shared logic)
# ---------------------------------------------------------------------------
def _render_card(name: str, status: dict, external_url: str) -> None:
    with st.container(border=True):
        s = status["status"]
        if s == "healthy":
            st.success(f"✅ **{name}**")
            st.caption("Status: Healthy")
            if "data" in status and isinstance(status["data"], dict):
                with st.expander("Details"):
                    st.json(status["data"])
        elif s == "unreachable":
            st.error(f"❌ **{name}**")
            st.caption("Status: Unreachable")
        elif s == "timeout":
            st.warning(f"⏱️ **{name}**")
            st.caption("Status: Timeout")
        else:
            st.warning(f"⚠️ **{name}**")
            st.caption(f"Status: {s}")
        st.caption(f"URL: {external_url}")

# ---------------------------------------------------------------------------
# Service status grid
# Build all placeholder containers first so the layout renders immediately,
# then run health checks one by one and update each placeholder in place.
# ---------------------------------------------------------------------------
st.markdown("### Service Status")

all_service_defs = []

for name, (internal_url, external_url, health_path) in http_services.items():
    all_service_defs.append(("http", name, internal_url, external_url, health_path, None, None))

for name, (host, port, ext_port) in tcp_services.items():
    all_service_defs.append(("tcp", name, host, f"{host}:{ext_port}", None, port, None))

# Pass 1: Create all placeholder cards (page fully visible before any check runs)
cols = st.columns(3)
placeholders = []
for idx, service_def in enumerate(all_service_defs):
    with cols[idx % 3]:
        ph = st.empty()
        with ph.container():
            with st.container(border=True):
                st.info(f"⏳ **{service_def[1]}**")
                st.caption("Status: Checking…")
        placeholders.append(ph)

# ---------------------------------------------------------------------------
# Quick Links  (rendered before health checks so the full page is visible)
# ---------------------------------------------------------------------------
st.divider()
st.markdown("### Quick Links")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown(f"[FastAPI Docs](http://localhost:{os.getenv('FASTAPI_PORT', '8000')}/docs)")
    st.markdown(f"[LangChain Docs](http://localhost:{os.getenv('LANGCHAIN_PORT', '8001')}/docs)")

with col2:
    st.markdown(f"[Airflow UI](http://localhost:{os.getenv('AIRFLOW_PORT', '8080')})")
    st.markdown(f"[MLflow UI](http://localhost:{os.getenv('MLFLOW_PORT', '5000')})")

with col3:
    st.markdown(f"[Grafana](http://localhost:{os.getenv('GRAFANA_PORT', '3000')})")
    st.markdown(f"[Prometheus](http://localhost:{os.getenv('PROMETHEUS_PORT', '9090')})")

with col4:
    st.markdown(f"[Gradio UI](http://localhost:{os.getenv('GRADIO_PORT', '7860')})")
    st.markdown(f"[MinIO Console](http://localhost:{os.getenv('MINIO_CONSOLE_PORT', '9001')})")

with col5:
    st.markdown(f"[dbt Docs](http://localhost:{os.getenv('DBT_PORT', '8002')})")
    st.markdown(f"[Weaviate](http://localhost:{os.getenv('WEAVIATE_PORT', '8081')})")

# Pass 2: Run all health checks in parallel — each card updates as soon as its check completes
def _run_check(service_def):
    kind, name, internal_url, external_url, health_path, port, _ = service_def
    if kind == "http":
        return check_service_health(internal_url, health_path=health_path)
    return check_tcp_health(internal_url, port)

with ThreadPoolExecutor(max_workers=len(all_service_defs)) as executor:
    futures = {executor.submit(_run_check, sd): i for i, sd in enumerate(all_service_defs)}
    for future in as_completed(futures):
        idx = futures[future]
        _, name, _, external_url, _, _, _ = all_service_defs[idx]
        with placeholders[idx].container():
            _render_card(name, future.result(), external_url)

# ---------------------------------------------------------------------------
# Detailed service information tabs
# ---------------------------------------------------------------------------
#st.divider()
#st.markdown("### Detailed Service Information")

#tab1, tab2 = st.tabs(["FastAPI", "LangChain"])

#with tab1:
#    try:
#        resp = __import__("requests").get("http://api:8000/", timeout=10)
#        api_info = resp.json() if resp.status_code == 200 else None
#    except Exception:
#        api_info = None
#    if api_info:
#        st.json(api_info)
#    else:
#        st.warning("Could not retrieve FastAPI information")

#with tab2:
#    langchain_info = get_service_info("http://langchain:8001")
#    if langchain_info:
#        st.json(langchain_info)
#    else:
#        st.warning("Could not retrieve LangChain information")

# ---------------------------------------------------------------------------
# Auto-refresh logic
# ---------------------------------------------------------------------------
if auto_refresh:
    st.sidebar.info("Auto-refreshing every 30 seconds...")
    time.sleep(30)
    st.rerun()

# Footer
st.sidebar.divider()
st.sidebar.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
