from app.agents.state import AssistantState
from app.agents.base import make_groq_llm
from app.prompts.language_prompt import PROMPT_LANGUAGE
import re, json

def node_language_agent(state: AssistantState) -> dict:
    """
    LanguageAgent:
      Input: itinerary activities
      Action: add local phrases, etiquette notes, safety tips per activity
      Output: translation snippets and culture tips appended to generated_content['language_annotations']
    """

    logs = state.get("logs", [])[:]
    generated = state.get("generated_content", {}) or {}
    itinerary = generated.get("revised_itinerary") or generated.get("preliminary_itinerary") or {}

    activities_summary = []
    days = itinerary.get("days", []) if isinstance(itinerary, dict) else []
    for d in days:
        for act in d.get("activities", []):
            activities_summary.append({"title": act.get("title"), "description": act.get("description")})

    prompt = PROMPT_LANGUAGE
    try:
        llm = make_groq_llm()
        resp = llm.invoke(prompt)

        parsed =getattr(resp, "content", resp)
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

    except Exception as e:
        logs.append({"step": "language", "error": str(e)})
        parsed = None

    generated["language_annotations"] = parsed
    logs.append({"step": "language", "annotated": len(parsed)})
    return {"generated_content": generated, "logs": logs}
