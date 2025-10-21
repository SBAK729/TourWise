import os
from typing import Dict, Any
from app.agents.base import make_groq_llm

# Directory containing your context files
DATA_DIR = "app/data"

def load_context_from_data() -> str:
    """
    Load all text files from DATA_DIR and combine them into a single context string.
    """
    context = []
    for filename in os.listdir(DATA_DIR):
        file_path = os.path.join(DATA_DIR, filename)
        if os.path.isfile(file_path) and filename.endswith((".txt", ".json")):
            with open(file_path, "r", encoding="utf-8") as f:
                context.append(f.read())
    return "\n".join(context)

def run_llm_chat(user_query: str, user_id: str) -> Dict[str, Any]:
    """
    Call Groq LLM with the user query and context from app/data.
    """

    # Load context from local files
    context = load_context_from_data()

    # Initialize LLM
    llm = make_groq_llm(temperature=0.4)

    # Prepare a prompt for the LLM
    prompt = f"""
You are a helpful AI travel assistant. Use the following context to answer the user's question:

Context:
{context}

User ID: {user_id}
Question: {user_query}

Answer concisely and clearly.
"""

    # Call the LLM
    response = llm.invoke(prompt)
    llm_output = getattr(response, "content", str(response))

    print("conversation:", llm_output)

    return {
        "response": llm_output,
        "mode": "conversation"
    }
