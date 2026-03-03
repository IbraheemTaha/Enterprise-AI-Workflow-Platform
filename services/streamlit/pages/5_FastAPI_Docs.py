"""
FastAPI Service Documentation & Live API Explorer
"""
import streamlit as st
import requests
import json
from utils.api_client import API_URL, get_fastapi, call_fastapi
import time


# Page config
st.set_page_config(
    page_title="FastAPI Docs - Enterprise AI Platform",
    page_icon="⚡",
    layout="wide"
)

# Sidebar navigation
with st.sidebar:
    st.title("Navigation")
    st.page_link("Home.py", label="🏠 Home")
    st.page_link("pages/1_Chat.py", label="📝 Chat")
    st.page_link("pages/2_System_Health.py", label="💚 System Health")
    st.page_link("pages/3_LangChain_Demo.py", label="🔗 LangChain Demo")
    st.page_link("pages/4_DBT_Platform.py", label="📊 DBT Platform")
    st.page_link("pages/5_FastAPI_Docs.py", label="⚡ FastAPI Docs")
    st.divider()
    #st.markdown(f"**API:** `{API_URL}`")
    #st.markdown(f"[OpenAPI Docs ↗]({API_URL}/docs)")
    st.caption(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")

st.title("⚡ FastAPI Service")
st.markdown("Multi-provider LLM gateway — OpenAI · Anthropic · Google Gemini · Amazon Bedrock")

tab1, tab2, tab3 = st.tabs(["Overview", "API Explorer", "Provider Guide"])

# ---------------------------------------------------------------------------
# Tab 1: Overview
# ---------------------------------------------------------------------------
with tab1:
    col_main, col_side = st.columns([2, 1])

    with col_main:
        st.markdown("""
## What is the FastAPI Service?

The FastAPI service is the **central LLM gateway** of this platform.
It routes chat requests to multiple AI providers through a single unified API,
so you can switch providers without changing your code.

---

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Service information |
| `GET` | `/health` | Which providers are configured |
| `GET` | `/v1/models?provider=<name>` | List models available to your API key |
| `POST` | `/v1/chat/completions` | Chat completion with any LLM |

---

## Chat Request Format

```json
{
  "provider": "anthropic",
  "model": "claude-sonnet-4-6",
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user",   "content": "Explain embeddings in one sentence."}
  ]
}
```

- `model` is **optional** — a default is applied per provider if omitted
- `messages` follows the OpenAI messages format (role + content)
- Full conversation history can be passed for multi-turn chat

## Chat Response Format

```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Embeddings are numerical vector representations..."
      }
    }
  ]
}
```

---

## Quick curl Examples

```bash
# Check which providers are configured
curl http://localhost:${FASTAPI_PORT:-8000}/health

# List available OpenAI models
curl "http://localhost:${FASTAPI_PORT:-8000}/v1/models?provider=openai"

# Send a chat message
curl -X POST http://localhost:${FASTAPI_PORT:-8000}/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -d '{"provider": "openai", "messages": [{"role": "user", "content": "Hello!"}]}'
```
""")

    with col_side:
        st.markdown("### Service Info")
        st.info(f"**Base URL:** `{API_URL}`\n\n**OpenAPI Docs:** `/docs`\n\n**Health check:** `/health`")

        st.markdown("### Architecture")
        st.code(
            "Streamlit / Gradio\n"
            "       │\n"
            "       ▼\n"
            " FastAPI :8000\n"
            "       │\n"
            "  ┌────┴────┐\n"
            "  │         │\n"
            " OpenAI  Anthropic\n"
            " Google    AWS",
            language=None
        )

        st.markdown("### Supported Providers")
        st.markdown("""
| Provider | Chat | Embeddings |
|----------|------|-----------|
| openai | ✅ | ✅ |
| anthropic | ✅ | ❌ |
| google | ✅ | ✅ |
| aws | ✅ | ❌ |
""")
        st.caption("Embeddings are used by LangChain for RAG. Chat works with any provider.")

# ---------------------------------------------------------------------------
# Tab 2: API Explorer
# ---------------------------------------------------------------------------
with tab2:
    st.markdown("### Live API Explorer")
    st.markdown("Select an endpoint, fill in parameters, and execute it against the running service.")

    endpoint = st.selectbox(
        "Endpoint",
        ["GET /health", "GET /v1/models", "POST /v1/chat/completions"]
    )

    st.divider()

    # --- GET /health ---
    if endpoint == "GET /health":
        st.markdown("**Returns which LLM providers have API keys configured.**")
        st.code(f"curl {API_URL}/health", language="bash")

        if st.button("▶ Execute", type="primary", key="health_btn"):
            with st.spinner("Calling /health..."):
                try:
                    data = get_fastapi("/health")
                    st.success("HTTP 200")
                    st.json(data)
                except Exception as e:
                    st.error(str(e))

    # --- GET /v1/models ---
    elif endpoint == "GET /v1/models":
        st.markdown("**Returns models available for a provider (queries the provider API live).**")
        provider = st.selectbox("Provider", ["openai", "anthropic", "google", "aws"], key="models_provider")
        st.code(f'curl "{API_URL}/v1/models?provider={provider}"', language="bash")

        if st.button("▶ Execute", type="primary", key="models_btn"):
            with st.spinner(f"Fetching models for {provider}..."):
                try:
                    data = get_fastapi("/v1/models", params={"provider": provider})
                    st.success("HTTP 200")
                    models = data.get("models", [])
                    st.markdown(f"**{len(models)} models available:**")
                    st.json(data)
                except Exception as e:
                    st.error(str(e))

    # --- POST /v1/chat/completions ---
    elif endpoint == "POST /v1/chat/completions":
        st.markdown("**Send a chat message to any supported LLM provider.**")

        col_left, col_right = st.columns(2)
        with col_left:
            provider = st.selectbox("Provider", ["openai", "anthropic", "google", "aws"], key="chat_provider")
        with col_right:
            model_input = st.text_input("Model (leave blank for default)", placeholder="e.g. gpt-4o-mini")

        system_msg = st.text_input(
            "System message (optional)",
            placeholder="You are a helpful assistant.",
            key="chat_system"
        )
        user_msg = st.text_area(
            "User message",
            value="Hello! What can you do?",
            key="chat_user"
        )

        # Build payload
        messages = []
        if system_msg:
            messages.append({"role": "system", "content": system_msg})
        messages.append({"role": "user", "content": user_msg})

        payload = {"provider": provider, "messages": messages}
        if model_input:
            payload["model"] = model_input

        st.markdown("**Generated curl command:**")
        st.code(
            f"curl -X POST {API_URL}/v1/chat/completions \\\n"
            f"  -H \"Content-Type: application/json\" \\\n"
            f"  -d '{json.dumps(payload)}'",
            language="bash"
        )

        if st.button("▶ Execute", type="primary", key="chat_btn"):
            with st.spinner("Calling LLM..."):
                try:
                    data = call_fastapi("/v1/chat/completions", payload, timeout=60)
                    st.success("HTTP 200")
                    answer = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                    if answer:
                        st.markdown("**Response:**")
                        st.markdown(answer)
                    with st.expander("Full JSON response"):
                        st.json(data)
                except Exception as e:
                    st.error(str(e))

# ---------------------------------------------------------------------------
# Tab 3: Provider Guide
# ---------------------------------------------------------------------------
with tab3:
    st.markdown("### Provider Setup Guide")
    st.info("Set API keys in your `.env` file and restart the services (`make restart`).")

    providers = [
        {
            "name": "🟢 OpenAI",
            "env_key": "OPENAI_API_KEY",
            "chat": True,
            "embeddings": True,
            "models": ["gpt-4o", "gpt-4o-mini", "o3-mini", "gpt-4-turbo"],
            "notes": "Most widely supported. Required for RAG if Google is not configured.",
            "get_key": "https://platform.openai.com/api-keys",
        },
        {
            "name": "🟣 Anthropic",
            "env_key": "ANTHROPIC_API_KEY",
            "chat": True,
            "embeddings": False,
            "models": ["claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5-20251001"],
            "notes": "Chat only. No embedding API — cannot be used for RAG ingestion.",
            "get_key": "https://console.anthropic.com/",
        },
        {
            "name": "🔵 Google",
            "env_key": "GOOGLE_API_KEY",
            "chat": True,
            "embeddings": True,
            "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
            "notes": "Supports both chat and embeddings. Interchangeable with OpenAI for RAG.",
            "get_key": "https://aistudio.google.com/app/apikey",
        },
        {
            "name": "🟠 AWS Bedrock",
            "env_key": "AWS_ACCESS_KEY_ID  +  AWS_SECRET_ACCESS_KEY  +  AWS_REGION",
            "chat": True,
            "embeddings": False,
            "models": [
                "anthropic.claude-3-5-sonnet-20241022-v2:0",
                "amazon.titan-text-express-v1",
                "meta.llama3-70b-instruct-v1:0",
            ],
            "notes": "Chat only via Bedrock. Models must be enabled in your AWS account first.",
            "get_key": "https://console.aws.amazon.com/iam/",
        },
    ]

    for p in providers:
        with st.expander(p["name"], expanded=False):
            col_a, col_b = st.columns([3, 2])
            with col_a:
                st.markdown(f"**`.env` variable:** `{p['env_key']}`")
                st.markdown(f"**Chat:** {'✅' if p['chat'] else '❌'}  &nbsp;&nbsp; **Embeddings (RAG):** {'✅' if p['embeddings'] else '❌ (chat only)'}")
                st.markdown(f"**Note:** {p['notes']}")
            with col_b:
                st.markdown("**Example model IDs:**")
                for m in p["models"]:
                    st.code(m)

    st.divider()
    st.markdown("### Model Selection Tips")
    st.markdown("""
- Use `GET /v1/models?provider=<name>` to see models available to your specific API key
- The `model` field is **optional** — defaults are applied per provider if omitted
- Model IDs must match the provider's format exactly (e.g. AWS includes version suffixes like `-v2:0`)
- For **RAG** (LangChain service), you must have `OPENAI_API_KEY` or `GOOGLE_API_KEY` —
  they are the only providers with embedding models
""")
