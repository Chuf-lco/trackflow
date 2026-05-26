from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = "sqlite:///./test.db"  # Default to SQLite for development
    LOG_LEVEL: str = "INFO"
    JWT_SECRET_KEY: Optional[str] = "testsecretkey"
    JWT_ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables

settings = Settings()