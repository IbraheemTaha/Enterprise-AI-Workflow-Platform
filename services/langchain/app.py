import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from langserve import add_routes
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Import chains
from chains.chat_chain import create_chat_chain
from chains.rag_chain import create_rag_chain
from utils.llm_factory import get_available_providers, get_embeddings
from utils.vector_store import get_vector_store, get_weaviate_client, create_collection_if_not_exists

# Initialize FastAPI app
app = FastAPI(
    title="LangChain Service API",
    version="1.0.0",
    description="LangChain service providing chat chains, RAG, and agent capabilities"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Weaviate client and collection
try:
    weaviate_client = get_weaviate_client()
    create_collection_if_not_exists(weaviate_client, "LangChainDocuments")
except Exception as e:
    print(f"Warning: Could not initialize Weaviate: {e}")
    weaviate_client = None


# Pydantic models
class IngestRequest(BaseModel):
    text: str
    metadata: Optional[Dict[str, Any]] = {}


class HealthResponse(BaseModel):
    status: str
    services: Dict[str, bool]
    available_providers: Dict[str, bool]


class DynamicChatMessage(BaseModel):
    role: str
    content: str


class DynamicChatRequest(BaseModel):
    messages: List[DynamicChatMessage]
    provider: str = "auto"
    model: Optional[str] = None


class DynamicRAGRequest(BaseModel):
    query: str
    provider: str = "auto"
    model: Optional[str] = None


# Add LangServe routes for chains — each registered independently so one failure
# does not prevent the other from being available.
try:
    chat_chain = create_chat_chain()
    add_routes(app, chat_chain, path="/chat", enable_feedback_endpoint=True)
    print("Chat chain registered at /chat")
except Exception as e:
    print(f"Warning: Could not initialize chat chain: {e}")

try:
    if weaviate_client:
        rag_chain = create_rag_chain(weaviate_client=weaviate_client)
        add_routes(app, rag_chain, path="/rag", enable_feedback_endpoint=True)
        print("RAG chain registered at /rag")
    else:
        print("Warning: Weaviate not available, RAG chain skipped")
except Exception as e:
    print(f"Warning: Could not initialize RAG chain: {e}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "LangChain Service",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/chat/invoke - Chat with LLM",
            "rag": "/rag/invoke - RAG query with vector search",
            "ingest": "/ingest - Ingest documents for RAG",
            "health": "/health - Service health check",
            "info": "/info - Service information",
            "docs": "/docs - OpenAPI documentation"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    providers = get_available_providers()

    health_status = {
        "status": "healthy",
        "services": {
            "weaviate": weaviate_client is not None,
            "postgres": bool(os.getenv("POSTGRES_URL")),
            "redis": bool(os.getenv("REDIS_URL")),
            "mlflow": bool(os.getenv("MLFLOW_TRACKING_URI"))
        },
        "available_providers": providers
    }

    return health_status


@app.get("/info")
async def info():
    """Service information and capabilities."""
    providers = get_available_providers()

    return {
        "service": "LangChain Service",
        "version": "1.0.0",
        "capabilities": {
            "chat": "Multi-provider chat with conversation memory",
            "rag": "Retrieval Augmented Generation with Weaviate",
            "agents": "Coming soon - Tool-using agents"
        },
        "available_providers": {
            provider: "available" if available else "not configured"
            for provider, available in providers.items()
        },
        "vector_store": "weaviate" if weaviate_client else "not available",
        "environment": os.getenv("LOG_LEVEL", "INFO")
    }


@app.post("/ingest")
async def ingest_document(request: IngestRequest):
    """
    Ingest a document into the vector store for RAG.

    Args:
        request: IngestRequest with text and optional metadata

    Returns:
        Success message with document ID
    """
    if not weaviate_client:
        raise HTTPException(status_code=503, detail="Weaviate not available")

    try:
        # Get embeddings and vector store
        embeddings = get_embeddings()
        vector_store = get_vector_store(
            embeddings=embeddings,
            client=weaviate_client,
            index_name="LangChainDocuments"
        )

        # Add document to vector store
        texts = [request.text]
        metadatas = [request.metadata]

        ids = vector_store.add_texts(texts=texts, metadatas=metadatas)

        return {
            "status": "success",
            "message": "Document ingested successfully",
            "document_ids": ids,
            "text_length": len(request.text)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {str(e)}")


@app.post("/chat/dynamic")
async def chat_dynamic(request: DynamicChatRequest):
    """
    Chat with a specific provider and model, selected at request time.
    Accepts the same provider/model values as the FastAPI /v1/models endpoint.
    """
    try:
        chain = create_chat_chain(provider=request.provider, model=request.model)
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        result = await chain.ainvoke({"messages": messages})
        return {"output": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/rag/dynamic")
async def rag_dynamic(request: DynamicRAGRequest):
    """
    RAG query with a specific provider and model, selected at request time.
    Accepts the same provider/model values as the FastAPI /v1/models endpoint.
    """
    if not weaviate_client:
        raise HTTPException(status_code=503, detail="Weaviate not available")
    try:
        chain = create_rag_chain(
            provider=request.provider,
            model=request.model,
            weaviate_client=weaviate_client,
        )
        result = await chain.ainvoke(request.query)
        return {"output": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "type": type(exc).__name__}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
