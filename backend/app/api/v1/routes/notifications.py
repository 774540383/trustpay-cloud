"""Notification routes."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/")
async def list_notifications(
    page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=50), unread_only: bool = False,
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user),
):
    q = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        q = q.where(Notification.is_read == False)
    total = (await db.execute(select(func.count(Notification.id)).where(Notification.user_id == current_user.id))).scalar_one()
    items = (await db.execute(q.order_by(Notification.created_at.desc()).offset((page-1)*per_page).limit(per_page))).scalars().all()
    import math
    return {"success": True, "data": {
        "items": [NotificationResponse.model_validate(n) for n in items],
        "total": total, "page": page, "pages": math.ceil(total/per_page) if total else 0
    }}


@router.post("/mark-all-read")
async def mark_all_read(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    from sqlalchemy import update
    from datetime import datetime, timezone
    await db.execute(
        update(Notification).where(Notification.user_id == current_user.id, Notification.is_read == False)
        .values(is_read=True, read_at=datetime.now(timezone.utc).isoformat())
    )
    return {"success": True, "message": "All notifications marked as read"}
