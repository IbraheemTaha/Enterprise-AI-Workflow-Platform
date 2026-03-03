import streamlit as st
from utils.api_client import call_langchain, get_fastapi, LANGCHAIN_URL
from pathlib import Path
import requests
import time

def load_readme(file_path: str) -> str:
    """Load markdown file content."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"*Error loading documentation: {str(e)}*"

# Page configuration
st.set_page_config(
    page_title="LangChain Demo - Enterprise AI Platform",
    page_icon="🔗",
    layout="wide"
)

st.title("🔗 LangChain Service Demo")
st.markdown("Explore LangChain capabilities: RAG, Chains, and more")

# ---------------------------------------------------------------------------
# Sidebar — provider/model selection (shared across all tabs)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("Navigation")
    st.page_link("Home.py", label="🏠 Home")
    st.page_link("pages/1_Chat.py", label="📝 Chat")
    st.page_link("pages/2_System_Health.py", label="💚 System Health")
    st.page_link("pages/3_LangChain_Demo.py", label="🔗 LangChain Demo")
    st.page_link("pages/4_DBT_Platform.py", label="📊 DBT Platform")
    st.page_link("pages/5_FastAPI_Docs.py", label="⚡ FastAPI Docs")
    st.divider()
    
    st.header("Settings")

    provider = st.selectbox(
        "Select LLM Provider",
        ["openai", "anthropic", "google", "aws"],
        key="langchain_provider"
    )

    # Initialize model cache
    if "langchain_models_cache" not in st.session_state:
        st.session_state.langchain_models_cache = {}

    fetch_error = None
    if provider not in st.session_state.langchain_models_cache:
        try:
            result = get_fastapi("/v1/models", params={"provider": provider})
            fetched = result.get("models", [])
            if fetched:
                st.session_state.langchain_models_cache[provider] = fetched
            else:
                fetch_error = f"No models returned for {provider}. Check the API key."
        except Exception as e:
            fetch_error = str(e)

    available_models = st.session_state.langchain_models_cache.get(provider, [])

    if available_models:
        model = st.selectbox("Select Model", available_models, key="langchain_model")
    else:
        model = None
        st.error(fetch_error or f"No models available for {provider}.")

    if st.button("Refresh Models"):
        st.session_state.langchain_models_cache.pop(provider, None)
        st.rerun()

    #st.divider()
    #st.markdown("### LangChain Service")
    #st.code(f"URL: {LANGCHAIN_URL}")

    st.divider()
    st.markdown("### Features")
    st.markdown("""
- **RAG Query**: Search and generate answers from your documents
- **Chat Chain**: Direct conversation with LLMs via LangChain
- **Document Ingestion**: Add documents to vector store
""")

    st.divider()
    st.markdown("### Tips")
    st.info("""
1. Ingest documents first
2. Then query them with RAG
3. Use Chat Chain for general conversations
""")

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Chat Chain", "RAG Query", "Document Ingestion", "Documentation"])

# ---------------------------------------------------------------------------
# Tab 1: Chat Chain
# ---------------------------------------------------------------------------
with tab1:
    st.header("Chat Chain")
    st.markdown("Direct chat using LangChain chat chain")

    if "langchain_messages" not in st.session_state:
        st.session_state.langchain_messages = []

    # Display chat messages
    for msg in st.session_state.langchain_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Type your message..."):
        if not model:
            st.error("No model selected. Choose a provider and model in the sidebar.")
        else:
            st.session_state.langchain_messages.append({"role": "user", "content": prompt})

            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        response = call_langchain(
                            "/chat/dynamic",
                            {
                                "messages": st.session_state.langchain_messages,
                                "provider": provider,
                                "model": model,
                            }
                        )

                        answer = response.get("output", str(response))
                        st.markdown(answer)
                        st.session_state.langchain_messages.append(
                            {"role": "assistant", "content": answer}
                        )

                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.langchain_messages.append(
                            {"role": "assistant", "content": error_msg}
                        )

    if st.button("Clear Chat"):
        st.session_state.langchain_messages = []
        st.rerun()


# ---------------------------------------------------------------------------
# Tab 2: RAG Query
# ---------------------------------------------------------------------------
with tab2:
    st.header("RAG (Retrieval Augmented Generation)")
    st.markdown("Query documents using vector search and LLM generation")

    query = st.text_area(
        "Enter your question:",
        placeholder="What is LangChain?",
        help="Ask a question about ingested documents"
    )

    col1, col2 = st.columns([1, 3])

    with col1:
        if st.button("🔍 Query RAG", type="primary"):
            if not model:
                st.error("No model selected. Choose a provider and model in the sidebar.")
            elif query:
                with st.spinner("Searching and generating answer..."):
                    try:
                        response = call_langchain(
                            "/rag/dynamic",
                            {"query": query, "provider": provider, "model": model}
                        )

                        with col2:
                            st.success("Query successful!")
                            st.markdown("### Answer:")
                            st.markdown(response.get("output", str(response)))

                    except Exception as e:
                        with col2:
                            st.error(f"Error: {str(e)}")
                            st.info("Make sure documents have been ingested first (see 'Document Ingestion' tab)")
            else:
                st.warning("Please enter a question")


# ---------------------------------------------------------------------------
# Tab 3: Document Ingestion
# ---------------------------------------------------------------------------
with tab3:
    st.header("Document Ingestion")
    st.markdown("Ingest documents into the vector store for RAG queries")
    st.info(
        "Embedding models are selected automatically based on available API keys "
        "(OpenAI → Google). The LLM provider/model above is not used during ingestion."
    )

    document_text = st.text_area(
        "Document Text:",
        placeholder="Enter the text you want to ingest...",
        height=200,
        help="This text will be stored in the vector database and can be queried using RAG"
    )

    col1, col2 = st.columns(2)

    with col1:
        source = st.text_input("Source", placeholder="e.g., documentation.pdf")

    with col2:
        category = st.text_input("Category", placeholder="e.g., product-docs")

    if st.button("📥 Ingest Document", type="primary"):
        if document_text:
            with st.spinner("Ingesting document..."):
                try:
                    response = requests.post(
                        f"{LANGCHAIN_URL}/ingest",
                        json={
                            "text": document_text,
                            "metadata": {
                                "source": source or "unknown",
                                "category": category or "general"
                            }
                        },
                        timeout=30
                    )

                    if response.status_code == 200:
                        st.success("Document ingested successfully!")
                        st.json(response.json())
                        st.info("You can now query this document using the RAG Query tab")
                    else:
                        st.error(f"Ingestion failed: {response.text}")

                except Exception as e:
                    st.error(f"Error: {str(e)}")
        else:
            st.warning("Please enter document text")


# ---------------------------------------------------------------------------
# Tab 4: Documentation
# ---------------------------------------------------------------------------
with tab4:
    st.header("📖 LangChain Service Documentation")

    readme_path = Path(__file__).parent.parent / "LANGCHAIN_README.md"
    content = load_readme(str(readme_path))
    st.markdown(content)

# Footer
st.sidebar.divider()
st.sidebar.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")