from os import getenv

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_HOST = getenv("APPLICATION_HOST", "0.0.0.0")
EXTERNAL_PORT = int(getenv("EXTERNAL_PORT", 8080))
INTERNAL_PORT = int(getenv("INTERNAL_PORT", 4000))
INTERNAL_API_TOKEN = getenv("INTERNAL_API_TOKEN", "very_secret_api_token")

PYTEST = bool(getenv("PYTEST", False))

DBMS = getenv("DBMS", "postgresql")
DB_DRIVER = getenv("DB_DRIVER", "asyncpg")
DB_MAX_CONNECTIONS = int(getenv("DB_MAX_CONNECTIONS", "5"))


class DatabaseSettings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def database_url(self) -> str:
        return f"{DBMS}+{DB_DRIVER}://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

DB_SETTINGS = DatabaseSettings()  # type: ignore
DATABASE_URL = DB_SETTINGS.database_url

IP_COOLING_PERIOD = int(getenv("IP_COOLING_PERIOD", 30))  # in days
REPEATED_BLACKLIST_IP_TTL = int(getenv("REPEATED_BLACKLIST_IP_TTL", 30))  # in days
