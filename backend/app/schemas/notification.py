"""Notification schemas."""
import uuid
from datetime import datetime
from pydantic import BaseModel


class NotificationResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    type: str
    channel: str
    title: str
    title_ar: str | None
    body: str
    body_ar: str | None
    is_read: bool
    created_at: datetime
