from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.auth import models, schemas, utils

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
