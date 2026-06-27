from enum import StrEnum


class NotificationChannel(StrEnum):
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"


class NotificationStatus(StrEnum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"
    CANCELLED = "cancelled"


class DeliveryAttemptStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
