"""KYC Document model."""
import uuid
from enum import Enum as PyEnum
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.session import Base
from app.models.base import UUIDMixin, TimestampMixin


class DocumentType(str, PyEnum):
    NATIONAL_ID_FRONT = "national_id_front"
    NATIONAL_ID_BACK = "national_id_back"
    PASSPORT = "passport"
    DRIVING_LICENSE = "driving_license"
    SELFIE = "selfie"
    SELFIE_WITH_ID = "selfie_with_id"
    PROOF_OF_ADDRESS = "proof_of_address"


class KYCDocument(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "kyc_documents"

    kyc_request_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("kyc_requests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_key: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    verification_notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    kyc_request: Mapped["KYCRequest"] = relationship("KYCRequest", back_populates="documents")
