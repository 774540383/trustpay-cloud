"""KYC Request model."""
import uuid
from enum import Enum as PyEnum
from sqlalchemy import String, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.base import UUIDMixin, TimestampMixin


class KYCStatus(str, PyEnum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REQUIRES_RESUBMISSION = "requires_resubmission"


class KYCRequest(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "kyc_requests"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    request_number: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(30), default=KYCStatus.PENDING, nullable=False)
    current_step: Mapped[int] = mapped_column(Integer, default=1)

    # Step 1 - Personal Info
    full_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    purpose: Mapped[str | None] = mapped_column(String(100), nullable=True)
    additional_details: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Review
    reviewed_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("admins.id"), nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reviewed_at: Mapped[str | None] = mapped_column(String(50), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="kyc_requests")
    documents: Mapped[list["KYCDocument"]] = relationship("KYCDocument", back_populates="kyc_request", lazy="select")
