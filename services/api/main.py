from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Enterprise AI API",
    description="Production AI API with multi-LLM support (OpenAI, Anthropic, Google Gemini, Amazon Nova)",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Enterprise AI Workflow Platform API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "services": {
            "api": True,
            "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
            "anthropic_configured": bool(os.getenv("ANTHROPIC_API_KEY")),
            "gemini_configured": bool(os.getenv("GOOGLE_API_KEY")),
            "amazon_nova_configured": bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))
        }
    }

@app.post("/v1/chat/completions")
async def chat_completions(request: dict):
    """Chat completion endpoint"""
    # Basic implementation - extend this
    return {
        "id": "chatcmpl-123",
        "object": "chat.completion",
        "created": 1677652288,
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": "This is a basic response. Extend this endpoint with LLM integration."
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
