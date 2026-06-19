"""KYC service."""
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.kyc_request import KYCRequest, KYCStatus
from app.models.kyc_document import KYCDocument, DocumentType
from app.models.user import User
from app.schemas.kyc import KYCStep1, AdminKYCReview
from app.core.errors import ConflictError, NotFoundError
import random, string


def generate_request_number() -> str:
    date_part = datetime.now(timezone.utc).strftime("%Y%m%d")
    rand_part = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    return f"KYC-{date_part}-{rand_part}"


class KYCService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def start_kyc(self, user: User) -> KYCRequest:
        existing = await self.db.execute(
            select(KYCRequest).where(
                KYCRequest.user_id == user.id,
                KYCRequest.status.in_([KYCStatus.PENDING, KYCStatus.UNDER_REVIEW])
            )
        )
        if existing.scalar_one_or_none():
            raise ConflictError("Active KYC request already exists")
        req = KYCRequest(user_id=user.id, request_number=generate_request_number(), status=KYCStatus.PENDING, current_step=1)
        self.db.add(req)
        await self.db.flush()
        return req

    async def submit_step1(self, request_id: uuid.UUID, user: User, data: KYCStep1) -> KYCRequest:
        req = await self._get_request(request_id, user.id)
        req.full_name = data.full_name
        req.phone_number = data.phone_number
        req.address = data.address
        req.purpose = data.purpose
        req.additional_details = data.additional_details
        req.current_step = 2
        await self.db.flush()
        return req

    async def attach_document(self, request_id: uuid.UUID, user_id: uuid.UUID, doc_type: DocumentType,
                               file_key: str, file_name: str, file_size: int, mime_type: str) -> KYCDocument:
        req = await self._get_request(request_id, user_id)
        doc = KYCDocument(kyc_request_id=req.id, document_type=doc_type, file_key=file_key,
                          file_name=file_name, file_size=file_size, mime_type=mime_type)
        self.db.add(doc)
        await self.db.flush()
        return doc

    async def submit_final(self, request_id: uuid.UUID, user: User) -> KYCRequest:
        req = await self._get_request(request_id, user.id)
        req.status = KYCStatus.UNDER_REVIEW
        req.submitted_at = datetime.now(timezone.utc).isoformat()
        req.current_step = 6
        user.kyc_status = "under_review"
        await self.db.flush()
        return req

    async def admin_review(self, request_id: uuid.UUID, admin_id: uuid.UUID, data: AdminKYCReview) -> KYCRequest:
        result = await self.db.execute(select(KYCRequest).where(KYCRequest.id == request_id))
        req = result.scalar_one_or_none()
        if not req:
            raise NotFoundError("KYC request")
        req.status = KYCStatus(data.status)
        req.reviewed_by_id = admin_id
        req.review_notes = data.review_notes
        req.rejection_reason = data.rejection_reason
        req.reviewed_at = datetime.now(timezone.utc).isoformat()
        from app.repositories.user import UserRepository
        await UserRepository(self.db).update(req.user_id, kyc_status=data.status)
        await self.db.flush()
        return req

    async def _get_request(self, request_id: uuid.UUID, user_id: uuid.UUID) -> KYCRequest:
        result = await self.db.execute(
            select(KYCRequest).where(KYCRequest.id == request_id, KYCRequest.user_id == user_id)
        )
        req = result.scalar_one_or_none()
        if not req:
            raise NotFoundError("KYC request")
        return req
