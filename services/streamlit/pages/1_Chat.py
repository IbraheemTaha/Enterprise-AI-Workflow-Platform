import streamlit as st
from utils.api_client import call_fastapi, get_fastapi
import time

# Page configuration
st.set_page_config(
    page_title="Chat - Enterprise AI Platform",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Chat Interface")
st.markdown("Multi-provider chat with AI assistants")
st.info(
    "This page sends messages directly to the **FastAPI** backend (`POST /v1/chat/completions`), "
    "which routes them to the selected LLM provider (OpenAI, Anthropic, Google, or AWS Bedrock). "
    "Select a provider and model in the sidebar to get started. "
    "For RAG (document-grounded answers), use the **🔗 LangChain Demo** page instead."
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "models_cache" not in st.session_state:
    st.session_state.models_cache = {}

# Sidebar for settings
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

    # Provider selection
    provider = st.selectbox(
        "Select LLM Provider",
        ["OpenAI", "Anthropic", "Google", "AWS"],
        index=0,
        help="Choose which LLM provider to use"
    )

    provider_key = provider.lower()

    # Fetch available models for selected provider (only cache successful non-empty results)
    fetch_error = None
    if provider_key not in st.session_state.models_cache:
        try:
            result = get_fastapi("/v1/models", params={"provider": provider_key})
            fetched = result.get("models", [])
            if fetched:
                st.session_state.models_cache[provider_key] = fetched
            else:
                fetch_error = f"No models returned for {provider}. Check that the API key is configured."
        except Exception as e:
            fetch_error = str(e)

    available_models = st.session_state.models_cache.get(provider_key, [])

    if available_models:
        model = st.selectbox(
            "Select Model",
            available_models,
            help="Choose a model from the provider's available models"
        )
    else:
        model = None
        st.error(fetch_error or f"No models available for {provider}.")

    if st.button("Refresh Models"):
        st.session_state.models_cache.pop(provider_key, None)
        st.rerun()

    st.divider()

    # Clear conversation button
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

    st.divider()

    if model:
        st.markdown("### Selected")
        st.info(f"**Provider:** {provider}  \n**Model:** {model}")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    if not model:
        st.error("No model selected. Please configure an API key for the selected provider.")
    else:
        # Add user message to session state
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    # Call FastAPI endpoint with full conversation history and selected model
                    response = call_fastapi(
                        "/v1/chat/completions",
                        {
                            "messages": st.session_state.messages,
                            "provider": provider_key,
                            "model": model,
                        }
                    )

                    # Extract content from response
                    if "choices" in response and len(response["choices"]) > 0:
                        assistant_message = response["choices"][0]["message"]["content"]
                    else:
                        assistant_message = "Error: Unexpected response format"

                    st.markdown(assistant_message)

                    # Add assistant message to session state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_message
                    })

                except Exception as e:
                    error_message = f"Error: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_message
                    })

# Display message count
if st.session_state.messages:
    st.sidebar.markdown(f"**Messages:** {len(st.session_state.messages)}")
# Footer
st.sidebar.divider()
st.sidebar.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
