from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str
    SUPABASE_ANON_KEY: str
    
    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Application
    PROJECT_NAME: str = "NDC UK Backend API"
    PROJECT_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = "your_email@gmail.com"
    SMTP_PASSWORD: str = "your_app_password"
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: str = "jpg,jpeg,png,pdf"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        return [ext.strip() for ext in self.ALLOWED_FILE_TYPES.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()