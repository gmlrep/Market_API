import logging
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent
ROOT_DIR: Path = Path(__file__).parent.parent.parent
load_dotenv()


class RedisSettings(BaseModel):
    host: str = os.getenv("HOST_REDIS", "localhost")
    port: int = int(os.getenv("PORT_REDIS") or "6379")
    password: str = os.getenv("PASSWORD_REDIS", "")


class DbSettings(BaseModel):
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_DB_PASSWORD", "")
    POSTGRES_USER: str = os.getenv("POSTGRES_DB_USER", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", os.getenv("POSTGRES_DB_USER", "postgres"))
    POSTGRES_HOST: str = os.getenv("POSTGRES_DB_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_DB_PORT", "5432")

    ENV_DATABASE_MAPPER: dict[str, str] = {
        "test": os.getenv("POSTGRES_TEST_DB", "test_market_api"),
    }

    echo: bool = False
    POOL_SIZE: int = 10
    POOL_OVERFLOW: int = 20
    POOL_TIMEOUT: int = 30

    PAGE: int = 1
    PAGE_SIZE: int = 20
    ORDERING: str = "-id"

    @property
    def db_name(self) -> str:
        env = (os.getenv("ENVIRONMENT") or os.getenv("ENV") or "").lower()
        if env in self.ENV_DATABASE_MAPPER:
            return self.ENV_DATABASE_MAPPER[env]
        return self.POSTGRES_DB

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.db_name}"
        )

    @property
    def db_url_sync(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.db_name}"
        )


class PasswordSalt(BaseModel):
    salt_static: str = os.getenv("SALT_STATIC", "test-static-salt")


class AuthJWT(BaseModel):
    private_key_path: Path = ROOT_DIR / "certs" / "jwt-private.pem"
    public_key_path: Path = ROOT_DIR / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES") or "30")
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS") or "30")


class MailSettings(BaseModel):
    password: str = os.getenv("EMAIL_PASSWORD", "")
    host: str = os.getenv("EMAIL_HOST", "")
    username: str = os.getenv("EMAIL_USERNAME", "")
    mail_from: str = os.getenv("EMAIL_FROM", "")
    port: int = int(os.getenv("EMAIL_PORT") or "465")


class CorsSettings(BaseSettings):
    IS_ALLOWED_CREDENTIALS: bool = bool(os.getenv("IS_ALLOWED_CREDENTIALS", "true"))
    ALLOWED_ORIGINS: list[str] = ["*"]
    ALLOWED_METHODS: list[str] = ["*"]
    ALLOWED_HEADERS: list[str] = ["*"]


class FastApiSettings(BaseModel):
    TITLE: str = "Market API"
    VERSION: str = "0.1.0"
    SUMMARY: str | None = "Market FastAPI project"
    DESCRIPTION: str | None = None
    DEBUG: bool = False
    DOCS_URL: str | None = os.getenv("DOCS_URL", "/docs")
    OPENAPI_URL: str | None = os.getenv("OPENAPI_URL", "/openapi.json")
    REDOC_URL: str | None = os.getenv("REDOC_URL", "/redoc")

    @property
    def set_backend_app_attributes(self) -> dict[str, Any]:
        return {
            "title": self.TITLE,
            "version": self.VERSION,
            "debug": self.DEBUG,
            "summary": self.SUMMARY,
            "description": self.DESCRIPTION,
            "docs_url": self.DOCS_URL,
            "openapi_url": self.OPENAPI_URL,
            "redoc_url": self.REDOC_URL,
        }


class ServerSettings(BaseSettings):
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = int(os.getenv("FAST_API_PORT") or os.getenv("API_PORT") or "9000")
    SERVER_WORKERS: int | None = None
    LOGGING_LEVEL: int = logging.INFO


class Settings(BaseSettings):
    page_limit: int = 2
    fast_api_port: int = int(os.getenv("FAST_API_PORT") or "9000")

    server: ServerSettings = ServerSettings()
    api: FastApiSettings = FastApiSettings()
    cors: CorsSettings = CorsSettings()
    mail_settings: MailSettings = MailSettings()
    db_settings: DbSettings = DbSettings()
    auth_jwt: AuthJWT = AuthJWT()
    password_salt: PasswordSalt = PasswordSalt()
    redis_settings: RedisSettings = RedisSettings()

    # alias used by repository / query helpers
    @property
    def database(self) -> DbSettings:
        return self.db_settings


settings = Settings()
