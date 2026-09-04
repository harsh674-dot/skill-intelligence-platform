import os
import sys
from pathlib import Path
from logging.config import fileConfig

from dotenv import load_dotenv

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context


# ============================================================
# PATH CONFIGURATION
# ============================================================

# Add the backend directory to Python's import path
backend_path = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_path))


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

# Load backend/.env
load_dotenv(backend_path / ".env")


# ============================================================
# ALEMBIC CONFIGURATION
# ============================================================

config = context.config


# Get DATABASE_URL from .env
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise RuntimeError(
        "DATABASE_URL is not set in backend/.env"
    )


# Tell Alembic to use our DATABASE_URL
config.set_main_option(
    "sqlalchemy.url",
    database_url
)


# ============================================================
# LOGGING
# ============================================================

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# ============================================================
# SQLALCHEMY MODELS
# ============================================================

from app.database import Base
from app.models import *

target_metadata = Base.metadata


# ============================================================
# OFFLINE MIGRATIONS
# ============================================================

def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.

    This generates SQL without creating a live database
    connection.
    """

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


# ============================================================
# ONLINE MIGRATIONS
# ============================================================

def run_migrations_online() -> None:
    """
    Run migrations in online mode.

    This creates a connection to PostgreSQL and applies
    migrations against the database.
    """

    connectable = engine_from_config(
        config.get_section(
            config.config_ini_section,
            {}
        ),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# ============================================================
# RUN MIGRATIONS
# ============================================================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()