# app/core/config.py
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sistema de Gestión Académica"
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///./academia.db"
    SECRET_KEY: str = "supersecretkey"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 días
    ALLOWED_HOSTS: List[str] = ["*"]


settings = Settings()