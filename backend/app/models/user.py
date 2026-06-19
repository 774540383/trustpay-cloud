"""User model."""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import String, Boolean, Integer, DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.base import UUIDMixin, TimestampMixin


class UserStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    role: Mapped[str] = mapped_column(String(30), default="user", nullable=False)
    kyc_status: Mapped[str] = mapped_column(String(30), default="not_started", nullable=False)
    referral_code: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True, index=True)
    referred_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    telegram_id: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True)
    is_email_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_phone_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    login_count: Mapped[int] = mapped_column(Integer, default=0)
    failed_login_attempts: Mapped[int] = mapped_column(Integer, default=0)
    loyalty_points: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    profile: Mapped["Profile"] = relationship("Profile", back_populates="user", uselist=False, lazy="select")
    wallet: Mapped["Wallet"] = relationship("Wallet", back_populates="user", uselist=False, lazy="select")
    kyc_requests: Mapped[list["KYCRequest"]] = relationship("KYCRequest", back_populates="user", lazy="select")
    tickets: Mapped[list["Ticket"]] = relationship("Ticket", back_populates="user", lazy="select")
    notifications: Mapped[list["Notification"]] = relationship("Notification", back_populates="user", lazy="select")
    audit_logs: Mapped[list["AuditLog"]] = relationship("AuditLog", back_populates="user", lazy="select")
    referrals_made: Mapped[list["Referral"]] = relationship(
        "Referral", foreign_keys="Referral.referrer_id", back_populates="referrer", lazy="select"
    )

    def __repr__(self):
        return f"<User {self.email}>"
