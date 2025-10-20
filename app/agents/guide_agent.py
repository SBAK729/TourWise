from typing import Dict, Any
from app.agents.state import AssistantState
from app.agents.base import make_groq_llm
from app.agents.retriever import node_retriever
from app.prompts.guide_prompt import PROMPT_GUIDE
import datetime
import os

def node_guide_agent(state: AssistantState) -> dict:
    
    logs = state.get("logs", [])[:]
    user_id = state.get("user_id", "unknown")
    prefs = state.get("generated_content", {}).get("preferences") or state.get("preferences") or {}
    query_text = f"build attractions and daily plan for preferences: {prefs}"

    retrieved = state.get("retrieved_chunks", [])

    if not retrieved:
        retrieved = node_retriever(state)

    llm = make_groq_llm()
    num_days = 1
    travel_dates = state.get("travel_dates")
    if travel_dates and isinstance(travel_dates, dict):
        start = travel_dates.get("start")
        end = travel_dates.get("end")
        try:
            start_dt = datetime.date.fromisoformat(start)
            end_dt = datetime.date.fromisoformat(end)
            num_days = (end_dt - start_dt).days + 1
        except Exception:
            num_days = prefs.get("duration_days", 1)

    prompt = PROMPT_GUIDE

    try:
        resp = llm.invoke(prompt)

        
        raw_text = None
        try:
            raw_text =getattr(resp, "content", resp)
        except Exception:
            raw_text = str(resp)
    except Exception as e:
        logs.append({"step": "guide", "error": str(e)})
        raw_text = None

    preliminary_itinerary = {}
    if raw_text:

        import json, re
        m = re.search(r"(\{[\s\S]*\})", raw_text)
        if m:
            try:
                preliminary_itinerary = json.loads(m.group(1))
            except Exception:
                preliminary_itinerary = {"raw": raw_text}
        else:
            preliminary_itinerary = {"raw": raw_text}
    else:
        preliminary_itinerary = {
            "days": [
                {
                    "date": None,
                    "activities": [
                        {"time": "09:00-12:00", "title": "Sightseeing: main attractions", "description": "Visit major sites", "duration_mins": 180}
                    ]
                }
            ]
        }

    logs.append({"step": "guide", "query_text": query_text, "num_days": num_days})
    return {"generated_content": {"preliminary_itinerary": preliminary_itinerary}, "logs": logs}
