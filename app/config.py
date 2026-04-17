from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str
    
    # AI Model
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    
    # Email
    SMTP_HOST: str = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = None
    SMTP_PASSWORD: str = None
    FROM_EMAIL: str = None
    
    # Teams
    TEAMS_WEBHOOK_URL: str = None
    
    # Web Search
    SERPAPI_KEY: str = None
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File handling
    MAX_FILE_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "uploads"
    EXPORT_DIR: str = "exports"
    
    # Debug and development
    DEBUG: bool = True
    SQL_DEBUG: bool = False
    
    # Application settings
    APP_NAME: str = "Automated Book Generation System"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    
    # API settings
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # Background task settings
    BACKGROUND_TASK_TIMEOUT: int = 300  # 5 minutes
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
