import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    APP_NAME: str = "Items API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # MongoDB settings
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME", "items_db")

    NY_LATITUDE: float = 40.7128
    NY_LONGITUDE: float = -74.0060
    NY_POSTCODE: str = "10001"

    ZIP_API_BASE_URL: str = "https://api.zippopotam.us/us"

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
