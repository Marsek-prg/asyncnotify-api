import uuid
from typing import Any

from app.models.event import Event
from app.schemas.event import EventCreate
from app.services.event_service import (
    count_events,
    create_event,
    get_event_by_id,
    list_events,
)


class FakeScalarResult:
    def __init__(self, items: list[Event]) -> None:
        self.items = items

    def all(self) -> list[Event]:
        return self.items


class FakeSession:
    def __init__(self) -> None:
        self.added: Event | None = None
        self.committed = False
        self.refreshed: Event | None = None
        self.scalars_statement: Any = None
        self.scalar_statement: Any = None
        self.items = [Event(event_type="order_created", source=None, payload={})]
        self.total = 1
        self.stored_id = uuid.uuid4()
        self.stored_event = Event(event_type="order_created", source=None, payload={})

    def add(self, instance: Event) -> None:
        self.added = instance

    def commit(self) -> None:
        self.committed = True

    def refresh(self, instance: Event) -> None:
        self.refreshed = instance

    def get(self, model: type[Event], event_id: uuid.UUID) -> Event | None:
        assert model is Event
        if event_id == self.stored_id:
            return self.stored_event
        return None

    def scalars(self, statement: Any) -> FakeScalarResult:
        self.scalars_statement = statement
        return FakeScalarResult(self.items)

    def scalar(self, statement: Any) -> int:
        self.scalar_statement = statement
        return self.total


def test_create_event_adds_commits_and_refreshes_event() -> None:
    db = FakeSession()
    event_data = EventCreate(
        event_type="order_created",
        source="stockflow-api",
        payload={"order_id": "123"},
    )

    event = create_event(db, event_data)

    assert event is db.added
    assert db.committed is True
    assert db.refreshed is event
    assert event.event_type == "order_created"
    assert event.source == "stockflow-api"
    assert event.payload == {"order_id": "123"}


def test_get_event_by_id_returns_event_or_none() -> None:
    db = FakeSession()

    assert get_event_by_id(db, db.stored_id) is db.stored_event
    assert get_event_by_id(db, uuid.uuid4()) is None


def test_list_events_returns_items_and_builds_statement() -> None:
    db = FakeSession()

    result = list_events(
        db,
        limit=20,
        offset=0,
        event_type="order_created",
        source="stockflow-api",
    )

    assert result == db.items
    assert db.scalars_statement is not None
    statement_text = str(db.scalars_statement)
    assert "ORDER BY events.created_at DESC" in statement_text
    assert "events.event_type" in statement_text
    assert "events.source" in statement_text


def test_count_events_returns_total_and_builds_statement() -> None:
    db = FakeSession()

    total = count_events(db, event_type="order_created", source="stockflow-api")

    assert total == 1
    assert db.scalar_statement is not None
    statement_text = str(db.scalar_statement)
    assert "count" in statement_text
    assert "events.event_type" in statement_text
    assert "events.source" in statement_text
