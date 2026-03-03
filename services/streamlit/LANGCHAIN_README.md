# LangChain Service

The LangChain service wraps LangChain into a REST API (`${LANGCHAIN_PORT:-8001}`).
It exposes three capabilities: **Chat Chain**, **RAG Query**, and **Document Ingestion**.

---

## RAG Workflow — 3 Steps

```
Step 1 — Ingest   →  POST /ingest
         Add text or documents to Weaviate (vector DB)

Step 2 — Query    →  POST /rag/dynamic
         Search stored documents + generate an answer

Step 3 — Chat     →  POST /chat/dynamic
         General conversation (no retrieval, full history)
```

> Weaviate starts **empty**. You must ingest documents before RAG queries return grounded answers.

---

## Endpoints Reference

### POST /chat/dynamic

Direct LLM chat via LangChain. Pass the full message history for multi-turn conversations.

**Request:**
```json
{
  "provider": "openai",
  "model": "gpt-4o-mini",
  "messages": [
    {"role": "user", "content": "Explain RAG in one paragraph"}
  ]
}
```

**Response:**
```json
{ "output": "RAG stands for Retrieval-Augmented Generation..." }
```

---

### POST /rag/dynamic

Searches documents stored in Weaviate, then generates an answer grounded in those results.

**Request:**
```json
{
  "provider": "openai",
  "model": "gpt-4o-mini",
  "query": "What is the return policy?"
}
```

**Response:**
```json
{ "output": "According to the ingested documents, the return policy is..." }
```

> Returns a generic or empty answer if the vector store is empty — ingest documents first.

---

### POST /ingest

Stores text in Weaviate for later RAG retrieval. The embedding model is selected
automatically based on available API keys (OpenAI first, then Google).

**Request:**
```json
{
  "text": "The return policy allows returns within 30 days with a receipt.",
  "metadata": {
    "source": "policy.pdf",
    "category": "support"
  }
}
```

**Response:**
```json
{ "status": "success", "chunks": 1 }
```

---

## curl Examples

```bash
# Chat via LangChain
curl -X POST http://localhost:${LANGCHAIN_PORT:-8001}/chat/dynamic \
  -H "Content-Type: application/json" \
  -d '{"provider": "anthropic", "model": "claude-haiku-4-5-20251001",
       "messages": [{"role": "user", "content": "Hello!"}]}'

# Ingest a document
curl -X POST http://localhost:${LANGCHAIN_PORT:-8001}/ingest \
  -H "Content-Type: application/json" \
  -d '{"text": "LangChain is a framework for building LLM applications.",
       "metadata": {"source": "intro.txt", "category": "docs"}}'

# RAG query
curl -X POST http://localhost:${LANGCHAIN_PORT:-8001}/rag/dynamic \
  -H "Content-Type: application/json" \
  -d '{"provider": "openai", "query": "What is LangChain?"}'
```

---

## Provider & Embedding Requirements

| Provider | Chat | Embeddings (RAG) | `.env` key |
|----------|------|-----------------|------------|
| openai | ✅ | ✅ | `OPENAI_API_KEY` |
| anthropic | ✅ | ❌ | `ANTHROPIC_API_KEY` |
| google | ✅ | ✅ | `GOOGLE_API_KEY` |
| aws | ✅ | ❌ | `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY` |

RAG ingestion requires an embedding model. Only **OpenAI** and **Google** provide embeddings —
Anthropic and AWS keys work for chat only.

---

## OpenAPI Docs

The full interactive API docs are available at:

```
http://localhost:${LANGCHAIN_PORT:-8001}/docs
```
