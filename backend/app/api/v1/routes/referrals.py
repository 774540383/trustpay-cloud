"""Referral routes."""
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.referral import Referral
from app.schemas.referral import ReferralResponse

router = APIRouter(prefix="/referrals", tags=["Referrals"])


@router.get("/my-stats")
async def my_referral_stats(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    total = (await db.execute(
        select(func.count(Referral.id)).where(Referral.referrer_id == current_user.id)
    )).scalar_one()
    paid = (await db.execute(
        select(func.count(Referral.id)).where(Referral.referrer_id == current_user.id, Referral.reward_paid == True)
    )).scalar_one()
    referrals = (await db.execute(
        select(Referral).where(Referral.referrer_id == current_user.id).order_by(Referral.created_at.desc())
    )).scalars().all()
    return {"success": True, "data": {
        "referral_code": current_user.referral_code,
        "total_referrals": total,
        "paid_rewards": paid,
        "items": [ReferralResponse.model_validate(r) for r in referrals],
    }}
