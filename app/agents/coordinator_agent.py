from app.agents.state import AssistantState
from app.agents.guide_agent import node_guide_agent
from app.agents.budget_agent import node_budget_agent
from app.agents.language_agent import node_language_agent
from app.agents.base import make_groq_llm
from app.prompts.coordinator_prompt import PROMPT_COORDINATOR
from typing import Dict, Any
import json
import re


def node_coordinator_agent(state: AssistantState) -> dict:
    """
    CoordinatorAgent:
      - Orchestrates: Guide -> Budget -> Language
      - Merges outputs into shared state
      - Calls LLM to finalize, validate, and summarize full itinerary
    """
    logs = state.get("logs", [])[:]

    # Run Guide Agent
    guide_out = node_guide_agent(state)
    merged_state = merge_state(state, guide_out)
    logs.extend(guide_out.get("logs", []))

    # Run Budget Agent
    budget_out = node_budget_agent(merged_state)
    merged_state = merge_state(merged_state, budget_out)
    logs.extend(budget_out.get("logs", []))

    # Run Language Agent
    language_out = node_language_agent(merged_state)
    merged_state = merge_state(merged_state, language_out)
    logs.extend(language_out.get("logs", []))

    # --- Prepare input for final LLM validation ---
    gen = merged_state.get("generated_content", {}) or {}
    llm_input = {
        "preliminary_itinerary": gen.get("preliminary_itinerary"),
        "budget_adjusted_itinerary": gen.get("revised_itinerary"),
        "cost_breakdown": gen.get("breakdown"),
        "language_annotations": gen.get("language_annotations"),
    }

    # --- LLM call for final coordination ---
    prompt = f"{PROMPT_COORDINATOR}\n\n### Input:\n{json.dumps(llm_input, indent=2)}"
    llm = make_groq_llm(model="llama-3.3-70b-versatile", temperature=0.2)
    response = llm.invoke(prompt)

    try:
        parsed =getattr(response, "content", response)
        json_match = re.search(r'\{.*\}', parsed, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
            except json.JSONDecodeError:
                parsed = {}
        else:
            parsed = {}

        # --- Defensive check ---
        if not isinstance(parsed, dict):
            parsed = {}
    except Exception:
        logs.append({"step": "coordinator", "error": "LLM output invalid JSON"})
        parsed = {
            "final_itinerary": gen.get("revised_itinerary", {}),
            "summary": {},
            "validation": {"warnings": ["Failed to parse LLM output"], "conflicts": []}
        }

    # Merge LLM results
    gen["final_itinerary"] = parsed.get("final_itinerary", {})
    gen["summary"] = parsed.get("summary", {})
    gen["validation"] = parsed.get("validation", {})

    logs.append({
        "step": "coordinator",
        "message": "Final itinerary validated and summarized by LLM",
        "summary": gen.get("summary", {})
    })

    merged_state["generated_content"] = gen
    merged_state["logs"] = logs
    return {"generated_content": gen, "logs": logs}


def merge_state(base_state: AssistantState, update: Dict[str, Any]) -> AssistantState:
    """
    Merge a partial update into base_state.
    - 'generated_content' → shallow merge
    - 'retrieved_chunks' → append
    - 'logs' → append
    """
    s = dict(base_state)
    s["logs"] = s.get("logs", []) + update.get("logs", [])
    gen = s.get("generated_content", {}) or {}
    new_gen = update.get("generated_content", {}) or {}
    s["generated_content"] = {**gen, **new_gen}

    if "retrieved_chunks" in update:
        s["retrieved_chunks"] = (s.get("retrieved_chunks") or []) + update.get("retrieved_chunks", [])

    for k, v in update.items():
        if k in ("logs", "generated_content", "retrieved_chunks"):
            continue
        s[k] = v
    return s
