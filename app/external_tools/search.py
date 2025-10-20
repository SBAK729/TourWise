from googlesearch import search

def supertool_search(query: str):
    """Fallback web search if RAG retrieval is weak."""
    results = []
    for url in search(query, num_results=3):
        results.append({"source": "google", "content": url})
    return results
