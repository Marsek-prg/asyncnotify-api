import importlib.util
from pathlib import Path

from sqlalchemy.orm import RelationshipProperty

from app.db.base import Base
from app.models import DeliveryAttempt, Event, Notification
from app.models.enums import (
    DeliveryAttemptStatus,
    NotificationChannel,
    NotificationStatus,
)


def test_model_modules_can_be_imported() -> None:
    assert Event.__tablename__ == "events"
    assert Notification.__tablename__ == "notifications"
    assert DeliveryAttempt.__tablename__ == "delivery_attempts"


def test_enum_values_are_correct() -> None:
    assert [item.value for item in NotificationChannel] == [
        "email",
        "sms",
        "webhook",
    ]
    assert [item.value for item in NotificationStatus] == [
        "pending",
        "queued",
        "processing",
        "sent",
        "failed",
        "retrying",
        "cancelled",
    ]
    assert [item.value for item in DeliveryAttemptStatus] == [
        "success",
        "failed",
        "retrying",
    ]


def test_metadata_contains_domain_tables() -> None:
    assert {"events", "notifications", "delivery_attempts"} <= set(
        Base.metadata.tables
    )


def test_main_relationships_are_declared() -> None:
    event_notifications = Event.__mapper__.relationships["notifications"]
    notification_event = Notification.__mapper__.relationships["event"]
    notification_attempts = Notification.__mapper__.relationships["attempts"]
    attempt_notification = DeliveryAttempt.__mapper__.relationships["notification"]

    assert isinstance(event_notifications, RelationshipProperty)
    assert event_notifications.mapper.class_ is Notification
    assert notification_event.mapper.class_ is Event
    assert notification_attempts.mapper.class_ is DeliveryAttempt
    assert attempt_notification.mapper.class_ is Notification


def test_initial_alembic_migration_exists() -> None:
    migration_path = Path(
        "alembic/versions/20260627_0001_create_notification_tables.py"
    )

    assert migration_path.exists()


def test_initial_alembic_migration_enums_do_not_auto_create_types() -> None:
    migration_path = Path(
        "alembic/versions/20260627_0001_create_notification_tables.py"
    )
    spec = importlib.util.spec_from_file_location("initial_migration", migration_path)

    assert spec is not None
    assert spec.loader is not None

    migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migration)

    assert migration.notification_channel.create_type is False
    assert migration.notification_status.create_type is False
    assert migration.delivery_attempt_status.create_type is False


def test_settings_exposes_database_url() -> None:
    from app.core.config import settings

    assert settings.app_name
    assert settings.app_version
    assert settings.database_url.startswith("postgresql+psycopg://")
