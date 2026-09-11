import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Sign Language Learning & Assessment Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Secrets & Tokens
    SECRET_KEY: str = os.getenv("SECRET_KEY", "SUPER_SECRET_SIGN_LANGUAGE_KEY_2026_CHANGE_IN_PROD")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Database Configuration (PostgreSQL Primary / SQLite Fallback)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sign_language.db")
    
    # AI / Model Configuration
    MODEL_PATH: str = os.getenv("MODEL_PATH", "app/ai/ml/models/gesture_model.joblib")
    MODEL_VERSION: str = "v1.0.0"
    MODEL_CONFIDENCE_THRESHOLD: float = 0.75
    AI_MODE: str = os.getenv("AI_MODE", "production")  # production | mock
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost"]

    # Server Network / Port Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "10000"))

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")

settings = Settings()
