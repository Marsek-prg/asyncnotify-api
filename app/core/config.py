from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AsyncNotify API"
    app_version: str = "0.1.0"
    database_url: str = (
        "postgresql+psycopg://asyncnotify:asyncnotify@postgres:5432/asyncnotify"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
