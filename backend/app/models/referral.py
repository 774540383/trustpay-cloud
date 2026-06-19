"""Referral model."""
import uuid
from decimal import Decimal
from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.base import UUIDMixin, TimestampMixin


class Referral(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "referrals"

    referrer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    referred_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(30), default="pending", nullable=False)
    reward_amount: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=Decimal("0.00"))
    reward_points: Mapped[int] = mapped_column(default=0)
    reward_paid: Mapped[bool] = mapped_column(default=False)
    reward_paid_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    referrer: Mapped["User"] = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_made")
    referred: Mapped["User"] = relationship("User", foreign_keys=[referred_id])
