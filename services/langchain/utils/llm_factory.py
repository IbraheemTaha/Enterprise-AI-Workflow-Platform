import os
from typing import Optional
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_aws import ChatBedrock
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.embeddings import Embeddings


def get_llm(provider: str = "auto", model: Optional[str] = None, temperature: float = 0.7, max_tokens: int = 1000) -> BaseChatModel:
    """
    Factory function to get LLM based on provider.

    Args:
        provider: LLM provider ("auto", "openai", "anthropic", "google", "aws").
                  "auto" selects the first available provider (openai → anthropic → google → aws).
        model: Specific model name to use. If None, uses the provider default.
        temperature: Sampling temperature
        max_tokens: Maximum tokens to generate

    Returns:
        BaseChatModel instance
    """
    if provider == "auto":
        if os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        elif os.getenv("ANTHROPIC_API_KEY"):
            provider = "anthropic"
        elif os.getenv("GOOGLE_API_KEY"):
            provider = "google"
        elif os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
            provider = "aws"
        else:
            raise ValueError(
                "No LLM provider available. Set at least one of: "
                "OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY, or AWS credentials."
            )

    provider = provider.lower()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return ChatOpenAI(
            model=model or "gpt-4o",
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key
        )

    elif provider == "anthropic":
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        return ChatAnthropic(
            model=model or "claude-sonnet-4-5-20250929",
            temperature=temperature,
            max_tokens=max_tokens,
            api_key=api_key
        )

    elif provider == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        return ChatGoogleGenerativeAI(
            model=model or "gemini-2.0-flash-exp",
            temperature=temperature,
            max_output_tokens=max_tokens,
            google_api_key=api_key
        )

    elif provider == "aws":
        return ChatBedrock(
            model_id=model or "us.amazon.nova-pro-v1:0",
            region_name=os.getenv("AWS_REGION", "us-east-1"),
            model_kwargs={"temperature": temperature, "max_tokens": max_tokens}
        )

    else:
        raise ValueError(f"Unsupported provider: {provider}. Supported: openai, anthropic, google, aws")


def get_embeddings(provider: str = "auto") -> Embeddings:
    """
    Factory function to get embeddings model based on provider.

    Args:
        provider: Embeddings provider ("auto", "openai", "google").
                  "auto" selects the first available provider (openai → google).

    Returns:
        Embeddings instance
    """
    if provider == "auto":
        if os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        elif os.getenv("GOOGLE_API_KEY"):
            provider = "google"
        else:
            raise ValueError(
                "No embedding provider available. "
                "Set OPENAI_API_KEY (OpenAI) or GOOGLE_API_KEY (Google) — "
                "Anthropic does not provide an embedding model."
            )

    provider = provider.lower()

    if provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        return OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=api_key
        )

    elif provider == "google":
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        return GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=api_key
        )

    else:
        raise ValueError(
            f"Unsupported embedding provider: {provider}. Supported: openai, google"
        )


def get_available_providers() -> dict:
    """
    Check which LLM providers are available based on environment variables.

    Returns:
        Dictionary with provider availability
    """
    return {
        "openai": bool(os.getenv("OPENAI_API_KEY")),
        "anthropic": bool(os.getenv("ANTHROPIC_API_KEY")),
        "google": bool(os.getenv("GOOGLE_API_KEY")),
        "aws": bool(os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"))
    }
