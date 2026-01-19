"""
Configuration settings for the Agno Orchestrator
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    APP_NAME: str = "Phonologic Agentic Orchestrator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # API Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: str = "https://ops.phonologic.cloud,http://localhost:3000,https://phonologic-ops-production.up.railway.app"
    
    # LLM Configuration (Anthropic Claude)
    ANTHROPIC_API_KEY: Optional[str] = None
    DEFAULT_MODEL: str = "claude-sonnet-4-20250514"
    
    # Search Provider (Serper.dev for better results)
    SERPER_API_KEY: Optional[str] = None
    
    # Agno Studio (optional - for visual debugging)
    # Get from: https://agno.com after signing up
    AGNO_API_KEY: Optional[str] = None
    
    # ClickUp Integration
    CLICKUP_API_TOKEN: Optional[str] = None
    CLICKUP_WORKSPACE_ID: Optional[str] = None
    CLICKUP_DEFAULT_LIST_ID: Optional[str] = None
    
    # Google Drive/Workspace
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    GOOGLE_SERVICE_ACCOUNT_JSON: Optional[str] = None
    GOOGLE_DRIVE_FOLDER_ID: Optional[str] = None
    
    # SendGrid Email
    SENDGRID_API_KEY: Optional[str] = None
    SENDGRID_FROM_EMAIL: str = "ops@phonologic.ca"
    SENDGRID_FROM_NAME: str = "Phonologic Operations"
    
    # Redis (Upstash)
    UPSTASH_REDIS_REST_URL: Optional[str] = None
    UPSTASH_REDIS_REST_TOKEN: Optional[str] = None
    
    # Security
    API_SECRET_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Module-level settings instance for direct import
settings = get_settings()
