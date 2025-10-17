from fastapi import FastAPI
from app.core.database import Base, engine
from app.auth import routes as auth_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TourismSense - Auth Demo")

@app.get("/")
def home():
    return {"message": "Tourism AI Backend is running 🚀"}


app.include_router(auth_routes.router)
