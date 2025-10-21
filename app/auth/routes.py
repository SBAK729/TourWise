from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.auth import models, schemas, utils
from app.agents.state import AssistantState
from app.agents.graph_langgraph import run_travel_graph
from app.agents.base import make_groq_llm
from app.ingestion.rag import run_llm_chat
import json
from fastapi.encoders import jsonable_encoder

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/signup", response_model=schemas.Token)
def signup(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = utils.hash_password(payload.password)
    user = models.User(email=payload.email, password_hash=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)
    token = utils.create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not utils.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = utils.create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me")
def me(current_user = Depends(utils.get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "created_at": current_user.created_at}


@router.post("/generate-itinerary")
async def generate_itinerary(request_data: schemas.Query):
    user_id = request_data.user_id
    user_input = request_data.user_input
    print("User:", user_id, "Query:", user_input)

    extractor_prompt = f"""
    You are an intent extraction model. Analyze the user's message and classify whether they want to:
    - have a travel-related conversation (e.g., ask questions, seek advice, or general chat), or
    - plan a trip (e.g., generate an itinerary or request travel details).

    Return structured JSON with this format:
    {{
      "intent_type": "plan_trip" | "conversation",
      "destination": "string or null",
      "duration_days": int or null,
      "budget_usd": int or null,
      "travel_dates": {{"start": "YYYY-MM-DD or null", "end": "YYYY-MM-DD or null"}},
      "preferences": {{"interests": ["string", ...] or []}}
    }}
    User query: "{user_input}"
    Respond with JSON only.
    """

    llm = make_groq_llm()
    response = llm.invoke(extractor_prompt)
    raw_output = getattr(response, "content", str(response))

    import re, json
    json_match = re.search(r'\{.*\}', raw_output, re.DOTALL)
    if not json_match:
        raise HTTPException(status_code=500, detail=f"LLM did not return valid JSON: {raw_output}")

    try:
        parsed = json.loads(json_match.group())
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"JSON parsing error: {e.msg}, raw: {raw_output}")

    intent_type = parsed.get("intent_type", "conversation")

    # Build base state
    state: AssistantState = {
        "user_id": user_id,
        "query": user_input,
        "preferences": parsed.get("preferences", {}),
        "travel_dates": parsed.get("travel_dates", {}),
        "budget": parsed.get("budget_usd"),
        "generated_content": {},
        "logs": [{"step": "intent_extraction", "parsed": parsed}],
    }

    # === Branch logic ===
    if intent_type == "plan_trip":
        # 🧭 Trip planning agent
        itinerary_result = run_travel_graph(state)

        from fastapi.encoders import jsonable_encoder
        safe_result = jsonable_encoder(itinerary_result)
        result = {
            "generated_content": safe_result["generated_content"]["revised_itinerary"],
            "language_annotations": safe_result["generated_content"]["language_annotations"],
            "savings_options": safe_result["generated_content"]["savings_options"],
            "estimated_total_cost_usd": safe_result["generated_content"]["estimated_total_cost_usd"],
            "breakdown": safe_result["generated_content"]["breakdown"],
        }
    else:
        # 💬 Conversational (RAG or LLM chat)
        result = run_llm_chat(user_query=user_input, user_id=user_id)

    return {
        "user_id": user_id,
        "query": user_input,
        "user_intent": parsed,
        "result": result,
    }
