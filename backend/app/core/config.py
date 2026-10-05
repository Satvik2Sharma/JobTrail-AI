import os
from typing import List, Union, Optional
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
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Server & Port for Render deployment
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./jobtrail.db")
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, v: str) -> str:
        if v and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v
    
    @property
    def is_sqlite(self) -> bool:
        return bool(self.DATABASE_URL and self.DATABASE_URL.startswith("sqlite"))
    
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
    
    # Supabase Storage Configuration
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL", None)
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = os.getenv("SUPABASE_SERVICE_ROLE_KEY", None)
    SUPABASE_STORAGE_BUCKET: str = os.getenv("SUPABASE_STORAGE_BUCKET", "resume-files")
    
    @property
    def is_supabase_storage_enabled(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_SERVICE_ROLE_KEY)
    
    # Local Uploads fallback
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
