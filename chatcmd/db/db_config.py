import os
import logging
from functools import lru_cache
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), ".env")
env_loaded = load_dotenv(env_path)


# for some reason using pydantic BaseSettings like described in
# https://fastapi.tiangolo.com/advanced/settings/#the-env-file
# does not work
# https://github.com/pydantic/pydantic/issues/1368
class Settings:
    PROJECT_NAME: str = "Shift Task"
    PROJECT_VERSION: str = "1.0.0"

    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)  # default postgres port is 5432
    POSTGRES_DB = os.getenv("POSTGRES_DB", "chat")
    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"


@lru_cache()
def get_settings():
    if not env_loaded:
        logging.fatal(
            "Could not load .env file. Connections to db will be unsuccessful"
        )
    return Settings()
