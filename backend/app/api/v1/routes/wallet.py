"""Wallet routes."""
import math
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.schemas.wallet import WalletResponse, TransactionResponse, PaginatedTransactions
from fastapi import HTTPException

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.get("/")
async def get_wallet(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    wallet = result.scalar_one_or_none()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    return {"success": True, "data": WalletResponse.model_validate(wallet)}


@router.get("/transactions")
async def get_transactions(
    page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user),
):
    wallet_result = await db.execute(select(Wallet).where(Wallet.user_id == current_user.id))
    wallet = wallet_result.scalar_one_or_none()
    if not wallet:
        return {"success": True, "data": PaginatedTransactions(items=[], total=0, page=page, per_page=per_page, pages=0)}
    total = (await db.execute(select(func.count(Transaction.id)).where(Transaction.wallet_id == wallet.id))).scalar_one()
    items = (await db.execute(
        select(Transaction).where(Transaction.wallet_id == wallet.id)
        .order_by(Transaction.created_at.desc()).offset((page-1)*per_page).limit(per_page)
    )).scalars().all()
    return {"success": True, "data": PaginatedTransactions(
        items=[TransactionResponse.model_validate(t) for t in items],
        total=total, page=page, per_page=per_page, pages=math.ceil(total/per_page) if total else 0
    )}
