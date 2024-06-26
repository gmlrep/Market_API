import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import BaseModel

BASE_DIR = Path(__file__).parent.parent

load_dotenv()


class RedisSettings(BaseModel):
    host: str = os.getenv('HOST_REDIS')
    port: int = int(os.getenv('PORT_REDIS'))
    password: str = os.getenv('PORT_REDIS')


class DbSettings(BaseModel):

    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_DB_PASSWORD')
    POSTGRES_USER: str = os.getenv('POSTGRES_DB_USER')
    POSTGRES_DB: str = os.getenv('POSTGRES_DB_USER')
    POSTGRES_HOST: str = os.getenv('POSTGRES_DB_HOST')
    POSTGRES_PORT: str = os.getenv('POSTGRES_DB_PORT')

    @property
    def db_url(self) -> str:
        return (f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@'
                f'{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}')

    # @property
    # def db_url(self) -> str:
    #     return f"sqlite+aiosqlite:///{BASE_DIR}/db/database.db"

    # db_url_test: str = f"sqlite+aiosqlite:///{BASE_DIR}/db/database_test.db"
    echo: bool = False


class PasswordSalt(BaseModel):
    salt_static: str = os.getenv('SALT_STATIC')


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / 'certs' / 'jwt-private.pem'
    public_key_path: Path = BASE_DIR / 'certs' / 'jwt-public.pem'
    algorithm: str = 'RS256'
    access_token_expire_minutes: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
    refresh_token_expire_days: int = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS'))


class MailSettings(BaseModel):
    password: str = os.getenv('EMAIL_PASSWORD')
    host: str = os.getenv('EMAIL_HOST')
    username: str = os.getenv('EMAIL_USERNAME')
    mail_from: str = os.getenv('EMAIL_FROM')
    port: int = int(os.getenv('EMAIL_PORT'))


class Settings(BaseSettings):

    fast_api_port: int = int(os.getenv('FAST_API_PORT'))

    page_limit: int = 2
    mail_settings: MailSettings = MailSettings()
    db_settings: DbSettings = DbSettings()
    auth_jwt: AuthJWT = AuthJWT()
    password_salt: PasswordSalt = PasswordSalt()
    redis_settings: RedisSettings = RedisSettings()


settings = Settings()
