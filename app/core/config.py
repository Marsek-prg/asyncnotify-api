from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AsyncNotify API"
    app_version: str = "0.1.0"
    database_url: str = (
        "postgresql+psycopg://asyncnotify:asyncnotify@localhost:5432/asyncnotify"
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
