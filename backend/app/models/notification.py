"""Notification model."""
import uuid
from enum import Enum as PyEnum
from sqlalchemy import String, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.base import UUIDMixin, TimestampMixin


class NotificationChannel(str, PyEnum):
    IN_APP = "in_app"
    TELEGRAM = "telegram"
    EMAIL = "email"
    PUSH = "push"


class NotificationType(str, PyEnum):
    KYC_APPROVED = "kyc_approved"
    KYC_REJECTED = "kyc_rejected"
    KYC_SUBMITTED = "kyc_submitted"
    TRANSACTION_COMPLETED = "transaction_completed"
    TICKET_REPLY = "ticket_reply"
    TICKET_RESOLVED = "ticket_resolved"
    REFERRAL_REWARD = "referral_reward"
    LOYALTY_UPGRADE = "loyalty_upgrade"
    GENERAL = "general"
    SECURITY_ALERT = "security_alert"


class Notification(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    channel: Mapped[str] = mapped_column(String(20), default=NotificationChannel.IN_APP, nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    title_ar: Mapped[str | None] = mapped_column(String(300), nullable=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    body_ar: Mapped[str | None] = mapped_column(Text, nullable=True)
    data_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    read_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[str | None] = mapped_column(String(50), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="notifications")
