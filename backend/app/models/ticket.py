"""Support Ticket model."""
import uuid
from enum import Enum as PyEnum
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.base import UUIDMixin, TimestampMixin


class TicketStatus(str, PyEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_USER = "waiting_user"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketPriority(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Ticket(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tickets"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(300), nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default=TicketStatus.OPEN, nullable=False)
    priority: Mapped[str] = mapped_column(String(20), default=TicketPriority.MEDIUM, nullable=False)
    assigned_to_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("admins.id"), nullable=True)
    resolved_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    satisfaction_rating: Mapped[int | None] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="tickets")
    messages: Mapped[list["TicketMessage"]] = relationship("TicketMessage", back_populates="ticket", lazy="select")
