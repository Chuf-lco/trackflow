from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/trackflow.db"  # Note: /data/ for Docker volume
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "changeme_in_prod"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()