from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.auth import routes as auth_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TourismSense - Auth Demo")

# ✅ Allow your frontend origin
origins = [
    "http://localhost:3000",  # your Next.js dev server
    "http://127.0.0.1:3000",  # optional, sometimes Next uses 127.0.0.1
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # specific origins only
    allow_credentials=True,
    allow_methods=["*"],            # allow POST, GET, OPTIONS, etc.
    allow_headers=["*"],            # allow all headers
)

@app.get("/")
def home():
    return {"message": "Tourism AI Backend is running 🚀"}


app.include_router(auth_routes.router)
