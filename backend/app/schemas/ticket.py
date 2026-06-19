"""Ticket schemas."""
import uuid
from datetime import datetime
from pydantic import BaseModel


class TicketCreate(BaseModel):
    subject: str
    body: str
    category: str | None = None
    priority: str = "medium"


class TicketMessageResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    sender_type: str
    body: str
    is_internal_note: bool
    attachment_name: str | None
    created_at: datetime


class TicketResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    ticket_number: str
    subject: str
    status: str
    priority: str
    category: str | None
    created_at: datetime
    messages: list[TicketMessageResponse] = []
