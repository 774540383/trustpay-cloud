"""KYC schemas."""
import uuid
from datetime import datetime
from pydantic import BaseModel


class KYCStep1(BaseModel):
    full_name: str
    phone_number: str
    address: str
    purpose: str
    additional_details: str | None = None


class KYCDocumentResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    document_type: str
    file_name: str
    is_verified: bool
    created_at: datetime


class KYCRequestResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    request_number: str
    status: str
    current_step: int
    full_name: str | None
    purpose: str | None
    submitted_at: str | None
    reviewed_at: str | None
    created_at: datetime
    documents: list[KYCDocumentResponse] = []


class AdminKYCReview(BaseModel):
    status: str  # approved | rejected | requires_resubmission
    review_notes: str | None = None
    rejection_reason: str | None = None
