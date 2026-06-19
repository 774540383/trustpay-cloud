"""Wallet model."""
import uuid
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import String, Numeric, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.base import UUIDMixin, TimestampMixin


class WalletStatus(str, PyEnum):
    ACTIVE = "active"
    FROZEN = "frozen"
    CLOSED = "closed"


class Wallet(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "wallets"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    account_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    balance: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=Decimal("0.00"), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="SAR", nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=WalletStatus.ACTIVE, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=True)
    daily_limit: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=Decimal("10000.00"))
    monthly_limit: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=Decimal("100000.00"))

    user: Mapped["User"] = relationship("User", back_populates="wallet")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="wallet", lazy="select")
