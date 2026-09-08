import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "Skill Intelligence Platform"
    PROJECT_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not set. Check backend/.env"
        )

    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Check backend/.env"
        )


settings = Settings()