import os
from typing import List, Union
try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ImportError:
    from pydantic import BaseModel as BaseSettings
    SettingsConfigDict = dict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "JobTrail-AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./jobtrail.db")
    
    # Security & Auth
    JWT_SECRET: str = os.getenv("JWT_SECRET", "jobtrail_ai_super_secret_jwt_key_2026_dev_mode_token")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")) # 24 hours
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []
    
    # Uploads
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024 # 10 MB
    
    # ML Recommendation Centralized Weights
    SEMANTIC_WEIGHT: float = 0.50
    SKILL_WEIGHT: float = 0.25
    ELIGIBILITY_WEIGHT: float = 0.15
    PREFERENCE_WEIGHT: float = 0.10
    
    # Sentence Transformer Model
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
