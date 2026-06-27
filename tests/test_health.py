from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.session import get_db
from app.main import app

client = TestClient(app)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_fastapi_metadata_uses_settings() -> None:
    assert app.title == settings.app_name
    assert app.version == settings.app_version


class FakeDatabaseSession:
    def __init__(self) -> None:
        self.executed_statements: list[str] = []

    def execute(self, statement: object) -> None:
        self.executed_statements.append(str(statement))


def test_database_health_check_uses_database_dependency() -> None:
    fake_db = FakeDatabaseSession()

    def override_get_db() -> FakeDatabaseSession:
        return fake_db

    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get("/health/db")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}
    assert fake_db.executed_statements == ["SELECT 1"]
