from pydantic import BaseSettings, Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Settings
    api_title: str = "AI Yoga Master API"
    api_version: str = "1.0.0"
    api_description: str = "Production-ready AI Yoga coaching backend"
    
    # Firebase
    firebase_service_account_path: str = Field(
        default="firebase-config.json",
        env="FIREBASE_SERVICE_ACCOUNT_PATH"
    )
    
    # Knowledge Base Paths
    knowledge_base_path: str = Field(
        default="knowledge/surya_namaskar.json",
        env="KNOWLEDGE_BASE_PATH"
    )
    safety_rules_path: str = Field(
        default="knowledge/safety_rules.json",
        env="SAFETY_RULES_PATH"
    )
    corrections_path: str = Field(
        default="knowledge/poses_corrections.json",
        env="CORRECTIONS_PATH"
    )
    
    # AI Settings
    llm_enabled: bool = Field(default=True, env="LLM_ENABLED")
    llm_model_name: str = Field(default="gpt-4", env="LLM_MODEL_NAME")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # CORS Settings
    cors_origins: list = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"