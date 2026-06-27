import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EventCreate(BaseModel):
    event_type: str = Field(..., min_length=1)
    source: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)

    @field_validator("event_type")
    @classmethod
    def validate_event_type(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("event_type must not be empty")
        return value


class EventRead(BaseModel):
    id: uuid.UUID
    event_type: str
    source: str | None
    payload: dict[str, Any]
    created_at: datetime
    processed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class EventListResponse(BaseModel):
    items: list[EventRead]
    total: int
    limit: int
    offset: int
