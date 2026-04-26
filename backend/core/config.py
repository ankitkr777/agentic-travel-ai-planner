from pydantic_settings import BaseSettings
from pydantic import validator
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "AgenticTravelPlanner"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: str = "*"
    SECRET_KEY: str = "change-me"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/travel_agent_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL_NAME: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.0
    FAISS_INDEX_PATH: str = "./faiss_index.pkl"
    RAG_TOP_K_RESULTS: int = 3
    XAI_API_KEY: str = ""
    AMADEUS_CLIENT_ID: str = ""
    AMADEUS_CLIENT_SECRET: str = ""
    
    class Config:
        env_file = ".env"

    @validator("DEBUG", pre=True, always=True)
    def set_debug_mode(cls, v, values):
        if values.get("ENVIRONMENT") == "production":
            return False
        return v

    @validator("ALLOWED_ORIGINS", pre=True, always=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v == "*":
            return [origin.strip() for origin in v.split(",")]
        return ["*"]

@lru_cache()
def get_settings() -> Settings:
    return Settings()