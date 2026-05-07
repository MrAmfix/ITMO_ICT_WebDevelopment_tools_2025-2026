import os

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/finance_db")
DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() in ("1", "true", "yes", "on")
