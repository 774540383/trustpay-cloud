"""KYC routes."""
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.services.kyc_service import KYCService
from app.schemas.kyc import KYCStep1, KYCRequestResponse, KYCDocumentResponse
from app.models.user import User
from app.models.kyc_document import DocumentType

router = APIRouter(prefix="/kyc", tags=["KYC"])


@router.post("/start", status_code=201)
async def start_kyc(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    req = await KYCService(db).start_kyc(current_user)
    return {"success": True, "data": KYCRequestResponse.model_validate(req)}


@router.post("/{request_id}/step1")
async def submit_step1(request_id: uuid.UUID, data: KYCStep1, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_active_user)):
    req = await KYCService(db).submit_step1(request_id, current_user, data)
    return {"success": True, "data": KYCRequestResponse.model_validate(req)}


@router.post("/{request_id}/documents")
async def upload_document(request_id: uuid.UUID, document_type: str = Form(...),
                          file: UploadFile = File(...),
                          db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_active_user)):
    file_key = f"kyc/{current_user.id}/{document_type}/{file.filename}"
    doc = await KYCService(db).attach_document(
        request_id, current_user.id, DocumentType(document_type),
        file_key, file.filename, file.size or 0, file.content_type or "",
    )
    return {"success": True, "data": KYCDocumentResponse.model_validate(doc)}


@router.post("/{request_id}/submit")
async def submit_kyc(request_id: uuid.UUID, db: AsyncSession = Depends(get_db),
                     current_user: User = Depends(get_current_active_user)):
    req = await KYCService(db).submit_final(request_id, current_user)
    return {"success": True, "data": KYCRequestResponse.model_validate(req), "message": "KYC submitted"}


@router.get("/my-requests")
async def my_requests(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.kyc_request import KYCRequest
    result = await db.execute(
        select(KYCRequest).where(KYCRequest.user_id == current_user.id)
        .options(selectinload(KYCRequest.documents))
        .order_by(KYCRequest.created_at.desc())
    )
    return {"success": True, "data": [KYCRequestResponse.model_validate(r) for r in result.scalars().all()]}
