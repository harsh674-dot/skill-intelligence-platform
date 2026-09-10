import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent
root_dir = backend_dir.parent

DEFAULT_DB_URL = "postgresql+psycopg://neondb_owner:npg_0poxjZXUFKc9@ep-wispy-dew-az55msvy-pooler.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require"

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_DB_URL)
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "sih26101-skill-intelligence-super-secret-jwt-key-2026")
    APP_NAME: str = "Skill Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_file=(str(backend_dir / ".env"), str(root_dir / ".env"), ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()