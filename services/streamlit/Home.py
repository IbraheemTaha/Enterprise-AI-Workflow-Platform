import streamlit as st
import os
import time
# Page configuration
st.set_page_config(
    page_title="Enterprise AI Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get environment variables
API_URL = os.getenv("API_URL", "http://api:8000")
LANGCHAIN_URL = os.getenv("LANGCHAIN_URL", "http://langchain:8001")

# Main page
st.title("🚀 Enterprise AI Workflow Platform")
st.markdown("### Advanced Web Interface")

st.markdown("""
Welcome to the Enterprise AI Workflow Platform! This platform provides comprehensive AI capabilities
for enterprise developers.

**Available Features:**
- **Chat** - Multi-provider chat interface (OpenAI, Anthropic, Google, AWS)
- **System Health** - Real-time monitoring of all platform services
- **LangChain Demo** - RAG, chains, and agent capabilities
- **DBT Platform** - Data transformation, analytics, and custom project creation
- **FastAPI Docs** - Live API explorer and provider setup guide

**Supported LLM Providers:**
- OpenAI GPT
- Anthropic Claude
- Google Gemini
- AWS Bedrock (Amazon Nova)
""")

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.page_link("Home.py", label="🏠 Home")
st.sidebar.page_link("pages/1_Chat.py", label="📝 Chat")
st.sidebar.page_link("pages/2_System_Health.py", label="💚 System Health")
st.sidebar.page_link("pages/3_LangChain_Demo.py", label="🔗 LangChain Demo")
st.sidebar.page_link("pages/4_DBT_Platform.py", label="📊 DBT Platform")
st.sidebar.page_link("pages/5_FastAPI_Docs.py", label="⚡ FastAPI Docs")
st.sidebar.divider()

st.sidebar.markdown("### Other Interfaces")
st.sidebar.markdown(f"- [Gradio UI](http://localhost:{os.getenv('GRADIO_PORT', '7860')}) - Simple interface")
st.sidebar.markdown(f"- [FastAPI Docs](http://localhost:{os.getenv('FASTAPI_PORT', '8000')}/docs) - API documentation")
st.sidebar.markdown(f"- [LangChain Docs](http://localhost:{os.getenv('LANGCHAIN_PORT', '8001')}/docs) - LangChain API")
st.sidebar.markdown(f"- [MLflow](http://localhost:{os.getenv('MLFLOW_PORT', '5000')}) - Experiment tracking")
st.sidebar.markdown(f"- [Airflow](http://localhost:{os.getenv('AIRFLOW_PORT', '8080')}) - Workflow orchestration")
st.sidebar.markdown(f"- [Grafana](http://localhost:{os.getenv('GRAFANA_PORT', '3000')}) - Monitoring dashboards")
st.sidebar.markdown(f"- [Prometheus](http://localhost:{os.getenv('PROMETHEUS_PORT', '9090')}) - Metrics")
st.sidebar.markdown(f"- [MinIO Console](http://localhost:{os.getenv('MINIO_CONSOLE_PORT', '9001')}) - Object storage")
st.sidebar.markdown(f"- [Weaviate](http://localhost:{os.getenv('WEAVIATE_PORT', '8081')}) - Vector database")
st.sidebar.markdown(f"- [dbt](http://localhost:{os.getenv('DBT_PORT', '8002')}) - Data transforms")

# Quick start section
st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("### 📝 Chat")
    st.markdown("Interactive chat with multiple LLM providers")
    if st.button("Go to Chat →"):
        st.switch_page("pages/1_Chat.py")

with col2:
    st.markdown("### 💚 System Health")
    st.markdown("Monitor all platform services")
    if st.button("Go to Health →"):
        st.switch_page("pages/2_System_Health.py")

with col3:
    st.markdown("### 🔗 LangChain")
    st.markdown("RAG and chain execution")
    if st.button("Go to LangChain →"):
        st.switch_page("pages/3_LangChain_Demo.py")

with col4:
    st.markdown("### 📊 DBT Platform")
    st.markdown("Data transformation & analytics")
    if st.button("Go to DBT →"):
        st.switch_page("pages/4_DBT_Platform.py")

col5, _, _, _ = st.columns(4)
with col5:
    st.markdown("### ⚡ FastAPI Docs")
    st.markdown("Live API explorer & provider guide")
    if st.button("Go to FastAPI Docs →"):
        st.switch_page("pages/5_FastAPI_Docs.py")

# Footer
st.divider()
st.markdown("Built with Streamlit | Enterprise AI Workflow Platform")


# Side Footer
st.sidebar.divider()
st.sidebar.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")