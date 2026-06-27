"""create notification tables

Revision ID: 20260627_0001
Revises:
Create Date: 2026-06-27 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "20260627_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

notification_channel = postgresql.ENUM(
    "email",
    "sms",
    "webhook",
    name="notification_channel",
    create_type=False,
)
notification_status = postgresql.ENUM(
    "pending",
    "queued",
    "processing",
    "sent",
    "failed",
    "retrying",
    "cancelled",
    name="notification_status",
    create_type=False,
)
delivery_attempt_status = postgresql.ENUM(
    "success",
    "failed",
    "retrying",
    name="delivery_attempt_status",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    notification_channel.create(bind, checkfirst=True)
    notification_status.create(bind, checkfirst=True)
    delivery_attempt_status.create(bind, checkfirst=True)

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=True),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_events_event_type", "events", ["event_type"])
    op.create_index("ix_events_source", "events", ["source"])

    op.create_table(
        "notifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("recipient", sa.String(length=255), nullable=False),
        sa.Column(
            "channel",
            notification_channel,
            nullable=False,
        ),
        sa.Column(
            "status",
            notification_status,
            nullable=False,
        ),
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("failed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_notifications_event_id", "notifications", ["event_id"])
    op.create_index("ix_notifications_recipient", "notifications", ["recipient"])
    op.create_index("ix_notifications_status", "notifications", ["status"])

    op.create_table(
        "delivery_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("notification_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            delivery_attempt_status,
            nullable=False,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "provider_response",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["notification_id"], ["notifications.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_delivery_attempts_notification_id",
        "delivery_attempts",
        ["notification_id"],
    )
    op.create_index("ix_delivery_attempts_status", "delivery_attempts", ["status"])


def downgrade() -> None:
    op.drop_index("ix_delivery_attempts_status", table_name="delivery_attempts")
    op.drop_index(
        "ix_delivery_attempts_notification_id",
        table_name="delivery_attempts",
    )
    op.drop_table("delivery_attempts")

    op.drop_index("ix_notifications_status", table_name="notifications")
    op.drop_index("ix_notifications_recipient", table_name="notifications")
    op.drop_index("ix_notifications_event_id", table_name="notifications")
    op.drop_table("notifications")

    op.drop_index("ix_events_source", table_name="events")
    op.drop_index("ix_events_event_type", table_name="events")
    op.drop_table("events")

    bind = op.get_bind()
    delivery_attempt_status.drop(bind, checkfirst=True)
    notification_status.drop(bind, checkfirst=True)
    notification_channel.drop(bind, checkfirst=True)
