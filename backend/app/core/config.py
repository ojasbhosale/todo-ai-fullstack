"""
Application configuration using Pydantic settings.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    DATABASE_URL: str
    SUPABASE_PROJECT_URL: str
    SUPABASE_SERVICE_ROLE_KEY: str
    
    # AI Configuration
    OPENAI_API_KEY: str
    GROQ_API_KEY: str
    
    # Application
    SECRET_KEY: str
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Smart Todo List API"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()