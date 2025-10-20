from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    pinecone_api_key: str
    GROQ_API_KEY: str
    MODEL: str

    class Config:
        env_file = ".env"

settings = Settings()
