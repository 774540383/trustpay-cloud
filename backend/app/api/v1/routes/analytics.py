"""Analytics routes."""
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.dependencies.auth import get_current_admin
from app.models.admin import Admin
from app.models.user import User
from app.models.kyc_request import KYCRequest
from app.models.ticket import Ticket
from app.models.transaction import Transaction

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/overview")
async def analytics_overview(db: AsyncSession = Depends(get_db), admin: Admin = Depends(get_current_admin)):
    total_users = (await db.execute(select(func.count(User.id)))).scalar_one()
    total_kyc = (await db.execute(select(func.count(KYCRequest.id)))).scalar_one()
    total_tickets = (await db.execute(select(func.count(Ticket.id)))).scalar_one()
    total_transactions = (await db.execute(select(func.count(Transaction.id)))).scalar_one()
    total_volume = (await db.execute(select(func.sum(Transaction.amount)))).scalar_one() or 0
    return {"success": True, "data": {
        "total_users": total_users, "total_kyc_requests": total_kyc,
        "total_tickets": total_tickets, "total_transactions": total_transactions,
        "total_transaction_volume": str(total_volume),
    }}
