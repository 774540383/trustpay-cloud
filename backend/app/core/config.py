"""Application configuration using Pydantic Settings."""
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "TrustPay"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_SECRET_KEY: str = "changeme"
    APP_ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    APP_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://trustpay:trustpay_pass@localhost:5432/trustpay_db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET_KEY: str = "changeme-use-a-real-secret-key-minimum-64-characters"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Admin
    ADMIN_EMAIL: str = "admin@trustpay.local"
    ADMIN_PASSWORD: str = "Admin@TrustPay2024!"

    # Storage
    STORAGE_ENDPOINT: str = "https://s3.amazonaws.com"
    STORAGE_ACCESS_KEY: str = ""
    STORAGE_SECRET_KEY: str = ""
    STORAGE_BUCKET: str = "trustpay-uploads"
    STORAGE_REGION: str = "us-east-1"

    # Email
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@trustpay.local"

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_KYC_BOT_TOKEN: str = ""

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_testing(self) -> bool:
        return self.APP_ENV == "testing"

    @field_validator("APP_ALLOWED_HOSTS", "APP_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_list(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except Exception:
                return [i.strip() for i in v.split(",")]
        return v


settings = Settings()
