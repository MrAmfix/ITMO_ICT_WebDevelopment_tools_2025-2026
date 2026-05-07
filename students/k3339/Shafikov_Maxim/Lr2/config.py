import os

from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB: str = os.getenv("POSTGRES_DB", "finance_db")
POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5433")

DATABASE_URL: str = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@localhost:{POSTGRES_PORT}/{POSTGRES_DB}"
)
DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() in ("1", "true", "yes", "on")
