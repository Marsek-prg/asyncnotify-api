import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://asyncnotify:asyncnotify@localhost:5432/asyncnotify",
    )


settings = Settings()
