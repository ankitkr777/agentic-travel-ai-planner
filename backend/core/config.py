from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache
from typing import Union, List

class Settings(BaseSettings):
    APP_NAME: str = "AgenticTravelPlanner"
    ENVIRONMENT: str = "local"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    ALLOWED_ORIGINS: Union[str, List[str]] = "*"
    SECRET_KEY: str = "change-me"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/travel_agent_db"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600
    DB_ECHO: bool = False

    XAI_API_KEY: str = ""
    OPENAI_MODEL_NAME: str = "grok-beta"
    OPENAI_TEMPERATURE: float = 0.0

    OPENWEATHER_API_KEY: str = "your-openweather-api-key"

    FAISS_INDEX_PATH: str = "./faiss_index.pkl"
    RAG_TOP_K_RESULTS: int = 3

    model_config = {"env_file": ".env", "extra": "ignore"}

    @field_validator("DEBUG", mode="before")
    @classmethod
    def set_debug_mode(cls, v, info):
        if info.data.get("ENVIRONMENT") == "production":
            return False
        return v

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and v != "*":
            return [origin.strip() for origin in v.split(",")]
        return v

@lru_cache()
def get_settings() -> Settings:
    return Settings()