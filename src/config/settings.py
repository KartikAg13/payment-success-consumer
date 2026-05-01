from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",  # Important for robustness
        case_sensitive=False,
    )

    # Required fields with no defaults
    redis_url: str
    database_url: str
    celery_broker_url: str
    celery_result_backend: str

    # Optional fields with defaults (for safety)
    environment: str = "development"
    log_level: str = "INFO"


# Singleton instance
settings = Settings()
