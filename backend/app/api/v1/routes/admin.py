"""Admin routes."""
import uuid, math
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.dependencies.auth import get_current_admin
from app.models.admin import Admin
from app.models.user import User
from app.models.kyc_request import KYCRequest, KYCStatus
from app.models.ticket import Ticket, TicketStatus
from app.schemas.user import UserResponse
from app.schemas.kyc import AdminKYCReview, KYCRequestResponse
from app.services.kyc_service import KYCService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
async def dashboard(db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    pending_kyc = (await db.execute(select(func.count(KYCRequest.id)).where(KYCRequest.status == KYCStatus.UNDER_REVIEW))).scalar_one()
    open_tickets = (await db.execute(select(func.count(Ticket.id)).where(Ticket.status == TicketStatus.OPEN))).scalar_one()
    return {"success": True, "data": {"total_users": total_users, "pending_kyc": pending_kyc, "open_tickets": open_tickets}}


@router.get("/users")
async def list_users(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100), status: str = Query(None),
                     db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    from app.repositories.user import UserRepository
    users, total = await UserRepository(db).list_all(offset=(page-1)*per_page, limit=per_page, status=status)
    return {"success": True, "data": {
        "items": [UserResponse.model_validate(u) for u in users],
        "total": total, "page": page, "pages": math.ceil(total/per_page) if total else 0
    }}


@router.get("/kyc")
async def list_kyc(status: str = Query(None), page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100),
                   db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    from sqlalchemy.orm import selectinload
    q = select(KYCRequest).options(selectinload(KYCRequest.documents))
    if status:
        q = q.where(KYCRequest.status == status)
    total = (await db.execute(select(func.count(KYCRequest.id)))).scalar_one()
    items = (await db.execute(q.order_by(KYCRequest.created_at.desc()).offset((page-1)*per_page).limit(per_page))).scalars().all()
    return {"success": True, "data": {
        "items": [KYCRequestResponse.model_validate(r) for r in items],
        "total": total, "page": page, "pages": math.ceil(total/per_page) if total else 0
    }}


@router.post("/kyc/{request_id}/review")
async def review_kyc(request_id: uuid.UUID, data: AdminKYCReview,
                     db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    req = await KYCService(db).admin_review(request_id, admin.id, data)
    return {"success": True, "data": KYCRequestResponse.model_validate(req)}
