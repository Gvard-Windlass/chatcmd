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
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")  # default postgres port is 5432
    POSTGRES_DB = os.getenv("POSTGRES_DB", "chat")
    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    def env_set(self) -> bool:
        return all(
            v is not None
            for v in [
                self.POSTGRES_USER,
                self.POSTGRES_PASSWORD,
                self.POSTGRES_SERVER,
                self.POSTGRES_PORT,
                self.POSTGRES_DB,
            ]
        )

    def describe_env(self) -> dict[str, str | None]:
        return {
            "user": self.POSTGRES_USER,
            "pwd": self.POSTGRES_PASSWORD,
            "server": self.POSTGRES_SERVER,
            "port": self.POSTGRES_PORT,
            "database": self.POSTGRES_DB,
            "url": self.DATABASE_URL,
        }


@lru_cache()
def get_settings():
    if not env_loaded:
        logging.warning(
            "Could not load .env file. Environment variables must be set by hand or connections to db will be unsuccessful"
        )
    return Settings()
