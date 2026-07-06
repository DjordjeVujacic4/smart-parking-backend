from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Smart Parking API"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    # Origins allowed to call the API (e.g. the Expo/React Native frontend).
    # Override via the CORS_ORIGINS env var as a JSON array, e.g.
    # CORS_ORIGINS='["http://localhost:8081","https://app.example.com"]'
    cors_origins: list[str] = [
        "http://localhost:8081",
        "http://127.0.0.1:8081",
    ]

    database_url: str

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    reservation_duration_minutes: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()
