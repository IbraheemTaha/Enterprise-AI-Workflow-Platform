from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
from utils.llm_factory import get_llm, get_embeddings
from utils.vector_store import get_vector_store, get_weaviate_client
from typing import List, Optional


def format_docs(docs: List[Document]) -> str:
    """Format documents for context."""
    return "\n\n".join(doc.page_content for doc in docs)


def create_rag_chain(provider: str = "auto", model: str = None, weaviate_client=None):
    """
    Create a RAG (Retrieval Augmented Generation) chain.

    Args:
        provider: LLM provider to use ("auto" selects first available).
        model: Specific model name. If None, the provider default is used.
        weaviate_client: Existing Weaviate client to reuse. Creates a new one if None.

    Returns:
        Runnable chain
    """
    # Initialize components
    llm = get_llm(provider=provider, model=model)
    embeddings = get_embeddings()  # auto-selects openai → google based on available keys

    # Reuse the provided client to avoid opening redundant gRPC connections
    client = weaviate_client if weaviate_client is not None else get_weaviate_client()
    vector_store = get_vector_store(embeddings=embeddings, client=client)

    # Create retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    # RAG prompt
    template = """You are a helpful AI assistant. Use the following context to answer the question.
If you cannot answer based on the context, say so clearly.

Context:
{context}

Question: {question}

Answer:"""

    prompt = ChatPromptTemplate.from_template(template)

    # Build RAG chain
    rag_chain = (
        RunnableParallel({
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        })
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain
