import os

from dotenv import load_dotenv

load_dotenv()


def get_bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


DATABASE_URL: str = os.getenv("DATABASE_URL")
DB_ECHO: bool = get_bool_env("DB_ECHO", True)

REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", 60))
