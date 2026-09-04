import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "Skill Intelligence Platform"
    PROJECT_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    if not DATABASE_URL:
        raise RuntimeError(
            "DATABASE_URL is not set. Check backend/.env"
        )


settings = Settings()