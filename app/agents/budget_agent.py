from app.agents.state import AssistantState
from app.agents.base import make_groq_llm
from app.prompts.budget_prompt import PROMPT_BUDGET
from typing import Dict, Any
import json
import re


def node_budget_agent(state: AssistantState) -> dict:
    """
    BudgetAgent:
    Receives the preliminary itinerary from GuideAgent and the user's budget.
    Calls the LLM to generate cost-optimized recommendations and a revised itinerary.
    """

    logs = state.get("logs", [])[:]
    generated = state.get("generated_content", {}) or {}
    prelim_itinerary = generated.get("preliminary_itinerary", {})

    budget_usd = state.get("budget")

    if not prelim_itinerary:
        logs.append({"step": "budget", "error": "missing preliminary_itinerary"})
        return {"generated_content": generated, "logs": logs}

 
    llm_input = {
        "itinerary": prelim_itinerary,
        "budget_usd": budget_usd,
    }

    prompt = f"{PROMPT_BUDGET}\n\n### Input:\n{json.dumps(llm_input, indent=2)}"

    llm = make_groq_llm()
    response = llm.invoke(prompt)

    try:
        parsed =getattr(response, "content", response)
        # print("parsed: ", parsed)
        json_match = re.search(r'\{.*\}', parsed, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
            except json.JSONDecodeError:
                parsed = {}
        else:
            parsed = {}

        if not isinstance(parsed, dict):
            parsed = {}
    except Exception:
        logs.append({"step": "budget", "error": "LLM output not valid JSON"})
        parsed = {
            "revised_itinerary": prelim_itinerary,
            "estimated_total_cost_usd": None,
            "breakdown": {},
            "savings_options": []
        }


    # Write LLM output into shared state
    generated["revised_itinerary"] = parsed["revised_itinerary"]
    generated["estimated_total_cost_usd"] = parsed["estimated_total_cost_usd"]
    generated["breakdown"] = parsed["breakdown"]
    generated["savings_options"] = parsed["savings_options"]

    logs.append({
        "step": "budget",
        "estimated_total_cost_usd": generated["estimated_total_cost_usd"],
    })

    return {"generated_content": generated, "logs": logs}
