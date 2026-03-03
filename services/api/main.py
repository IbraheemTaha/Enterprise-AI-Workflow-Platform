from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="Enterprise AI API",
    description="Production AI API with multi-LLM support (OpenAI, Anthropic, Google Gemini, Amazon Bedrock)",
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


@app.get("/v1/models")
async def list_models(provider: str):
    """Return available chat models for the specified provider by querying the provider's API."""
    provider = provider.lower()

    try:
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise HTTPException(status_code=503, detail="OPENAI_API_KEY not configured")
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            all_models = client.models.list()
            chat_prefixes = ("gpt-", "o1", "o3", "o4", "chatgpt-")
            exclude_terms = ("instruct", "embedding", "tts", "whisper", "realtime", "audio", "moderation")
            models = sorted([
                m.id for m in all_models.data
                if any(m.id.startswith(p) for p in chat_prefixes)
                and not any(t in m.id for t in exclude_terms)
            ])

        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY not configured")
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            models_page = client.models.list()
            models = [m.id for m in models_page.data]

        elif provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise HTTPException(status_code=503, detail="GOOGLE_API_KEY not configured")
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            models = [
                m.name.replace("models/", "")
                for m in genai.list_models()
                if "generateContent" in m.supported_generation_methods
            ]

        elif provider == "aws":
            if not (os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY")):
                raise HTTPException(status_code=503, detail="AWS credentials not configured")
            import boto3
            client = boto3.client(
                "bedrock",
                region_name=os.getenv("AWS_REGION", "us-east-1"),
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            )
            resp = client.list_foundation_models(byOutputModality="TEXT")
            models = [
                m["modelId"] for m in resp["modelSummaries"]
                if "ON_DEMAND" in m.get("inferenceTypesSupported", [])
            ]

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported provider '{provider}'. Use: openai, anthropic, google, aws"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"provider": provider, "models": models}


def _openai_chat(messages: list, model: str = "gpt-4o") -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return resp.choices[0].message.content


def _anthropic_chat(messages: list, model: str = "claude-sonnet-4-5-20250929") -> str:
    import anthropic
    system_text = ""
    conversation = []
    for msg in messages:
        if msg["role"] == "system":
            system_text = msg["content"]
        else:
            conversation.append(msg)
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    kwargs = dict(
        model=model,
        max_tokens=1024,
        messages=conversation,
    )
    if system_text:
        kwargs["system"] = system_text
    resp = client.messages.create(**kwargs)
    return resp.content[0].text


def _google_chat(messages: list, model: str = "gemini-2.0-flash-exp") -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gen_model = genai.GenerativeModel(model)
    history = []
    last_user_msg = ""
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        if msg == messages[-1] and msg["role"] == "user":
            last_user_msg = msg["content"]
        else:
            history.append({"role": role, "parts": [msg["content"]]})
    chat = gen_model.start_chat(history=history)
    resp = chat.send_message(last_user_msg)
    return resp.text


def _aws_chat(messages: list, model: str = "amazon.nova-pro-v1:0") -> str:
    import boto3
    client = boto3.client(
        "bedrock-runtime",
        region_name=os.getenv("AWS_REGION", "us-east-1"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )
    resp = client.converse(
        modelId=model,
        messages=[
            {"role": m["role"], "content": [{"text": m["content"]}]}
            for m in messages if m["role"] != "system"
        ],
    )
    return resp["output"]["message"]["content"][0]["text"]


@app.post("/v1/chat/completions")
async def chat_completions(request: dict):
    """Chat completion endpoint supporting OpenAI, Anthropic, Google, and AWS providers."""
    messages = request.get("messages", [])
    provider = request.get("provider", "openai").lower()
    model = request.get("model")

    if not messages:
        raise HTTPException(status_code=400, detail="messages field is required")

    try:
        if provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise HTTPException(status_code=503, detail="OPENAI_API_KEY not configured")
            kwargs = {"messages": messages}
            if model:
                kwargs["model"] = model
            content = _openai_chat(**kwargs)

        elif provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise HTTPException(status_code=503, detail="ANTHROPIC_API_KEY not configured")
            kwargs = {"messages": messages}
            if model:
                kwargs["model"] = model
            content = _anthropic_chat(**kwargs)

        elif provider == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise HTTPException(status_code=503, detail="GOOGLE_API_KEY not configured")
            kwargs = {"messages": messages}
            if model:
                kwargs["model"] = model
            content = _google_chat(**kwargs)

        elif provider == "aws":
            if not (os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY")):
                raise HTTPException(status_code=503, detail="AWS credentials not configured")
            kwargs = {"messages": messages}
            if model:
                kwargs["model"] = model
            content = _aws_chat(**kwargs)

        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported provider '{provider}'. Use: openai, anthropic, google, aws"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "id": "chatcmpl-enterprise",
        "object": "chat.completion",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop"
        }],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
