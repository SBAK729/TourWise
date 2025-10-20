from app.agents.state import AssistantState
from typing import Dict, Any, List, Optional
import os


def node_retriever(state: AssistantState) -> dict:

    query = state.get("query", "")
    logs = state.get("logs", [])[:]

    if not query:
        logs.append({"step": "retriever", "error": "no query provided"})
        return {"retrieved_chunks": [], "logs": logs}

    index_name = os.getenv("PINECONE_INDEX_NAME", "tourwise")


    try:
        from langchain.vectorstores import Pinecone
        from sentence_transformers import SentenceTransformer
        from app.agents.base import get_pinecone_client

        client = get_pinecone_client()
        embeddings = SentenceTransformer("all-MiniLM-L6-v2")
        index = client.Index(index_name)
        vectordb = Pinecone(index, embeddings.embed_query, index_name)
        docs = vectordb.similarity_search(query, k=5)
    
    except Exception as e:
        logs.append({"step": "retriever", "error": str(e)})
        return {"retrieved_chunks": [], "logs": logs}

    retrieved: List[Dict[str, Any]] = []
    for i, d in enumerate(docs):
        meta = getattr(d, "metadata", {}) or {}
        retrieved.append({
            "id": meta.get("id", f"chunk_{i}"),
            "source": meta.get("source", "pinecone"),
            "text": getattr(d, "page_content", str(d))
        })

    logs.append({"step": "retriever", "query": query, "retrieved": len(retrieved)})
    return {"retrieved_chunks": retrieved, "logs": logs}
