from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.auth import routes as auth_routes

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TourismSense - Auth Demo")


origins = [
    "http://localhost:3000",  
    "http://127.0.0.1:3000", 
    "https://tourwise-ui.vercel.app/", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          
    allow_credentials=True,
    allow_methods=["*"],            
    allow_headers=["*"],            
)

@app.get("/")
def home():
    return {"message": "Tourism AI Backend is running 🚀"}


app.include_router(auth_routes.router)
