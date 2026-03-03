# How to Use This Chat

## Quick Start

1. **Click "Additional inputs"** — the accordion below the chat input box
2. **Select a Provider** — choose from OpenAI, Anthropic, Google, or AWS
3. **Click "↻ Refresh Models"** — loads the model list for that provider
4. **Select a Model** — pick from the dropdown
5. **Start chatting** — type your message and press Enter

---

## Providers

| Provider | `.env` key | Typical models |
|----------|-----------|----------------|
| **openai** | `OPENAI_API_KEY` | gpt-4o, gpt-4o-mini, o3-mini |
| **anthropic** | `ANTHROPIC_API_KEY` | claude-sonnet-4-6, claude-haiku-4-5-20251001 |
| **google** | `GOOGLE_API_KEY` | gemini-2.0-flash, gemini-1.5-pro |
| **aws** | `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` | Bedrock: Claude, Titan, Llama |

Add your API keys to `.env` and restart the service (`make restart`) to activate a provider.

---

## Tips

- The model list is fetched **live** from the provider's API — only models available to
  your API key appear in the dropdown
- Conversations have **multi-turn memory** — context is preserved across messages
- To start a fresh conversation, reload the page
- The **API Health** tab lets you check which LLM providers are configured in the FastAPI backend

---

## Troubleshooting

**"No model selected"**
→ Open "Additional inputs", click ↻ Refresh Models, then select a model.

**Empty model list after refresh**
→ Your API key for that provider may be missing or invalid. Check `.env`.

**Slow or no response**
→ Large models (GPT-4o, Claude Opus) take longer. Try a smaller model like `gpt-4o-mini`
  or `claude-haiku-4-5-20251001`.

**API not available (health check fails)**
→ Run `make ps` to check if the `api` container is running, and `make logs` to inspect errors.

---

## Other Interfaces

This platform also includes:
- **Streamlit** — advanced multi-page UI with LangChain RAG, dbt analytics, and health dashboard
- **FastAPI Docs** — interactive OpenAPI docs at `/docs`
- **LangChain API** — RAG and chain orchestration service
