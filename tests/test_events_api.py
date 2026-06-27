import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any

from fastapi.testclient import TestClient

from app.api.v1.routes import events
from app.db.session import get_db
from app.main import app

client = TestClient(app)


def make_event(**overrides: Any) -> SimpleNamespace:
    data = {
        "id": uuid.uuid4(),
        "event_type": "order_created",
        "source": "stockflow-api",
        "payload": {"order_id": "123"},
        "created_at": datetime(2026, 6, 27, 12, 0, tzinfo=UTC),
        "processed_at": None,
    }
    data.update(overrides)
    return SimpleNamespace(**data)


def override_get_db() -> object:
    return object()


def test_create_event_returns_created_event(monkeypatch: Any) -> None:
    created_event = make_event()

    def fake_create_event(db: object, event_data: object) -> SimpleNamespace:
        return created_event

    monkeypatch.setattr(events.event_service, "create_event", fake_create_event)
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.post(
            "/api/v1/events",
            json={
                "event_type": "order_created",
                "source": "stockflow-api",
                "payload": {"order_id": "123"},
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["id"] == str(created_event.id)
    assert response.json()["event_type"] == "order_created"


def test_create_event_rejects_empty_event_type() -> None:
    response = client.post(
        "/api/v1/events",
        json={"event_type": "   ", "payload": {}},
    )

    assert response.status_code == 422


def test_list_events_returns_list_response(monkeypatch: Any) -> None:
    event = make_event()

    def fake_list_events(
        db: object,
        limit: int,
        offset: int,
        event_type: str | None = None,
        source: str | None = None,
    ) -> list[SimpleNamespace]:
        assert limit == 10
        assert offset == 5
        assert event_type == "order_created"
        assert source == "stockflow-api"
        return [event]

    def fake_count_events(
        db: object,
        event_type: str | None = None,
        source: str | None = None,
    ) -> int:
        assert event_type == "order_created"
        assert source == "stockflow-api"
        return 1

    monkeypatch.setattr(events.event_service, "list_events", fake_list_events)
    monkeypatch.setattr(events.event_service, "count_events", fake_count_events)
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get(
            "/api/v1/events",
            params={
                "limit": 10,
                "offset": 5,
                "event_type": "order_created",
                "source": "stockflow-api",
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": str(event.id),
                "event_type": "order_created",
                "source": "stockflow-api",
                "payload": {"order_id": "123"},
                "created_at": "2026-06-27T12:00:00Z",
                "processed_at": None,
            }
        ],
        "total": 1,
        "limit": 10,
        "offset": 5,
    }


def test_get_event_returns_one_event(monkeypatch: Any) -> None:
    event_id = uuid.uuid4()
    event = make_event(id=event_id)

    def fake_get_event_by_id(db: object, requested_id: uuid.UUID) -> SimpleNamespace:
        assert requested_id == event_id
        return event

    monkeypatch.setattr(events.event_service, "get_event_by_id", fake_get_event_by_id)
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get(f"/api/v1/events/{event_id}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["id"] == str(event_id)


def test_get_event_returns_404_for_missing_event(monkeypatch: Any) -> None:
    def fake_get_event_by_id(db: object, requested_id: uuid.UUID) -> None:
        return None

    monkeypatch.setattr(events.event_service, "get_event_by_id", fake_get_event_by_id)
    app.dependency_overrides[get_db] = override_get_db
    try:
        response = client.get(f"/api/v1/events/{uuid.uuid4()}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    assert response.json() == {"detail": "Event not found"}


def test_events_router_is_registered() -> None:
    openapi_paths = app.openapi()["paths"]

    assert "post" in openapi_paths["/api/v1/events"]
    assert "get" in openapi_paths["/api/v1/events"]
    assert "get" in openapi_paths["/api/v1/events/{event_id}"]
