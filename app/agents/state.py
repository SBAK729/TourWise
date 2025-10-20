from typing import TypedDict, List, Optional, Dict, Any

class AssistantState(TypedDict, total=False):
    user_id: str
    query: str

    preferences: Optional[Dict[str, Any]]
    travel_dates: Optional[Dict[str, str]]
    budget: Optional[float]

    retrieved_chunks: Optional[List[Dict[str, Any]]]
    conversation_response: Optional[str]
    generated_content: Optional[Dict[str, Any]]

    logs: Optional[List[Dict[str, Any]]]
