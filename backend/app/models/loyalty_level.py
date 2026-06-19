"""Loyalty Level model."""
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base
from app.models.base import UUIDMixin, TimestampMixin


class LoyaltyLevel(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "loyalty_levels"

    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name_ar: Mapped[str] = mapped_column(String(50), nullable=False)
    level_order: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    min_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_points: Mapped[int | None] = mapped_column(Integer, nullable=True)
    color: Mapped[str] = mapped_column(String(20), default="#808080")
    icon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cashback_rate: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0.00"))
    referral_bonus_multiplier: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("1.00"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description_ar: Mapped[str | None] = mapped_column(String(500), nullable=True)
