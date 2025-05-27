import os

from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "Widget API"

    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "widget_db")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "secret")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 14

    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    CORS_MAX_AGE: int = 600

    RATE_LIMIT_ANON_REQUESTS: int = Field(default=30)
    RATE_LIMIT_AUTH_REQUESTS: int = Field(default=100)
    RATE_LIMIT_WINDOW_SECONDS: int = Field(default=60)

    SSL_KEYFILE: str = os.getenv("SSL_KEYFILE")
    SSL_CERTFILE: str = os.getenv("SSL_CERTFILE")

    @property
    def CORS_ALLOW_ORIGINS(self) -> list[str]:
        origins_str = os.getenv("CORS_ALLOW_ORIGINS", "*")
        return [origin.strip() for origin in origins_str.split(',')]


settings = Settings()
