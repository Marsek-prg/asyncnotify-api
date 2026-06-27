import uuid

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.schemas.event import EventCreate


def _apply_event_filters(
    statement: Select[tuple[Event]] | Select[tuple[int]],
    event_type: str | None = None,
    source: str | None = None,
) -> Select[tuple[Event]] | Select[tuple[int]]:
    if event_type is not None:
        statement = statement.where(Event.event_type == event_type)
    if source is not None:
        statement = statement.where(Event.source == source)
    return statement


def create_event(db: Session, event_data: EventCreate) -> Event:
    event = Event(
        event_type=event_data.event_type,
        source=event_data.source,
        payload=event_data.payload,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_event_by_id(db: Session, event_id: uuid.UUID) -> Event | None:
    return db.get(Event, event_id)


def list_events(
    db: Session,
    limit: int,
    offset: int,
    event_type: str | None = None,
    source: str | None = None,
) -> list[Event]:
    statement = (
        select(Event)
        .order_by(Event.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    statement = _apply_event_filters(statement, event_type=event_type, source=source)
    return list(db.scalars(statement).all())


def count_events(
    db: Session,
    event_type: str | None = None,
    source: str | None = None,
) -> int:
    statement = select(func.count()).select_from(Event)
    statement = _apply_event_filters(statement, event_type=event_type, source=source)
    return db.scalar(statement) or 0
