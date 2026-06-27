import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.event import EventCreate, EventListResponse, EventRead
from app.services import event_service

router = APIRouter(prefix="/api/v1/events", tags=["events"])


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(
    event_data: EventCreate,
    db: Annotated[Session, Depends(get_db)],
) -> EventRead:
    return event_service.create_event(db, event_data)


@router.get("", response_model=EventListResponse)
def list_events(
    db: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    event_type: str | None = None,
    source: str | None = None,
) -> EventListResponse:
    items = event_service.list_events(
        db,
        limit=limit,
        offset=offset,
        event_type=event_type,
        source=source,
    )
    total = event_service.count_events(db, event_type=event_type, source=source)
    return EventListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{event_id}", response_model=EventRead)
def get_event(
    event_id: uuid.UUID,
    db: Annotated[Session, Depends(get_db)],
) -> EventRead:
    event = event_service.get_event_by_id(db, event_id)
    if event is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found",
        )
    return event
