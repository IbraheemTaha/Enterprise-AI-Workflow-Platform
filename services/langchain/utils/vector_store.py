import os
import weaviate
from weaviate.classes.init import Auth
from langchain_weaviate import WeaviateVectorStore
from langchain_core.embeddings import Embeddings
from typing import Optional


def get_weaviate_client():
    """
    Initialize and return Weaviate client.

    Returns:
        Weaviate client instance
    """
    weaviate_url = os.getenv("WEAVIATE_URL", "http://weaviate:8080")

    # Connect to Weaviate
    client = weaviate.connect_to_custom(
        http_host=weaviate_url.replace("http://", "").replace("https://", "").split(":")[0],
        http_port=int(weaviate_url.split(":")[-1]) if ":" in weaviate_url.split("//")[1] else 8080,
        http_secure=weaviate_url.startswith("https"),
        grpc_host=weaviate_url.replace("http://", "").replace("https://", "").split(":")[0],
        grpc_port=50051,
        grpc_secure=weaviate_url.startswith("https"),
    )

    return client


def get_vector_store(
    embeddings: Embeddings,
    index_name: str = "LangChainDocuments",
    client: Optional[weaviate.WeaviateClient] = None
) -> WeaviateVectorStore:
    """
    Initialize and return Weaviate vector store.

    Args:
        embeddings: Embeddings model to use
        index_name: Name of the Weaviate index
        client: Optional Weaviate client (creates new if not provided)

    Returns:
        WeaviateVectorStore instance
    """
    if client is None:
        client = get_weaviate_client()

    vector_store = WeaviateVectorStore(
        client=client,
        index_name=index_name,
        text_key="text",
        embedding=embeddings,
    )

    return vector_store


def create_collection_if_not_exists(client, collection_name: str = "LangChainDocuments"):
    """
    Create Weaviate collection if it doesn't exist.

    Args:
        client: Weaviate client
        collection_name: Name of the collection to create
    """
    try:
        # Check if collection exists
        if not client.collections.exists(collection_name):
            # Create collection with vectorizer configuration
            client.collections.create(
                name=collection_name,
                vectorizer_config=None,  # We'll provide vectors ourselves
            )
            print(f"Created collection: {collection_name}")
        else:
            print(f"Collection already exists: {collection_name}")
    except Exception as e:
        print(f"Error creating collection: {e}")
