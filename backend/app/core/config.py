"""
Application configuration using Pydantic settings (Pydantic v2.x compatible).
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    SUPABASE_PROJECT_URL: str = Field(..., env="SUPABASE_PROJECT_URL")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")
    
    # AI Configuration
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    GROQ_API_KEY: str = Field(..., env="GROQ_API_KEY")
    
    # Application
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="production", env="ENVIRONMENT")
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Smart Todo List API"
    
    # Optional: Model config for loading environment variables
    model_config = SettingsConfigDict(case_sensitive=True)


# Create a single instance to be imported and used app-wide
settings = Settings()
