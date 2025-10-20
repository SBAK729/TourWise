import os
from typing import Optional
from dotenv import load_dotenv


load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL =os.getenv("MODEL")
DEFAULT_TEMPERATURE = float(0.15)
DEFAULT_MAX_TOKENS = int(512)

def make_groq_llm(model: Optional[str] = None, temperature: float = DEFAULT_TEMPERATURE):
    """
    Returns a ChatGroq-like object from langchain_groq or langchain integration.
    """
    model = model or GROQ_MODEL
    if not GROQ_API_KEY:
        raise EnvironmentError("GROQ_API_KEY not set in environment.")
    try:
        from langchain_groq.chat_models import ChatGroq
    except Exception as e:
        raise RuntimeError("Please install langchain-groq (pip install -U langchain-groq) to use Groq LLM integrations.") from e

    return ChatGroq(model=model, groq_api_key=GROQ_API_KEY, temperature=temperature)

def get_pinecone_client(api_key: Optional[str] = None):
    api_key = api_key or os.getenv("PINECONE_API_KEY")
    if not api_key:
        raise EnvironmentError("PINECONE_API_KEY not set.")
    try:
        from pinecone import Pinecone
    except Exception as e:
        raise RuntimeError("Please install pinecone-client (pip install pinecone-client) to use Pinecone.") from e

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

    return pc