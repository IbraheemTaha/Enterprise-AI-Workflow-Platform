from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage
from utils.llm_factory import get_llm


# Create chat prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant for the Enterprise AI Workflow Platform. "
     "You can help users with various tasks and answer their questions."),
    MessagesPlaceholder(variable_name="messages"),
])


def _convert_messages(input_data: dict) -> dict:
    """Convert dict-formatted messages to LangChain message objects."""
    converted = []
    for msg in input_data.get("messages", []):
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            converted.append(HumanMessage(content=content))
        elif role == "assistant":
            converted.append(AIMessage(content=content))
    return {"messages": converted}


def create_chat_chain(provider: str = "auto", model: str = None):
    """
    Create a basic chat chain.

    Args:
        provider: LLM provider to use
        model: Specific model name. If None, the provider default is used.

    Returns:
        Runnable chain
    """
    llm = get_llm(provider=provider, model=model)

    chain = RunnableLambda(_convert_messages) | prompt | llm | StrOutputParser()

    return chain


# Default chain instance
try:
    chat_chain = create_chat_chain()
except Exception as e:
    print(f"Warning: Could not initialize default chat chain: {e}")
    chat_chain = None
