"""Transaction model."""
import uuid
from decimal import Decimal
from enum import Enum as PyEnum
from sqlalchemy import String, Numeric, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.base import UUIDMixin, TimestampMixin


class TransactionType(str, PyEnum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    FEE = "fee"
    REFUND = "refund"
    REWARD = "reward"


class TransactionStatus(str, PyEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REVERSED = "reversed"


class Transaction(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "transactions"

    wallet_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False, index=True)
    reference_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=TransactionStatus.PENDING, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    fee: Mapped[Decimal] = mapped_column(Numeric(18, 8), default=Decimal("0.00"))
    currency: Mapped[str] = mapped_column(String(10), default="SAR", nullable=False)
    balance_before: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_wallet_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("wallets.id"), nullable=True)

    wallet: Mapped["Wallet"] = relationship("Wallet", foreign_keys=[wallet_id], back_populates="transactions")
