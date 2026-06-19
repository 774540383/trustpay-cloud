"""Ticket routes."""
import uuid, random, string
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.models.ticket import Ticket, TicketStatus
from app.models.ticket_message import TicketMessage
from app.schemas.ticket import TicketCreate, TicketResponse

router = APIRouter(prefix="/tickets", tags=["Support Tickets"])


def gen_ticket_number() -> str:
    return "TK-" + "".join(random.choices(string.digits, k=8))


@router.post("/", status_code=201)
async def create_ticket(data: TicketCreate, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_active_user)):
    ticket = Ticket(user_id=current_user.id, ticket_number=gen_ticket_number(),
                    subject=data.subject, category=data.category, priority=data.priority)
    db.add(ticket)
    await db.flush()
    msg = TicketMessage(ticket_id=ticket.id, sender_type="user", sender_id=current_user.id, body=data.body)
    db.add(msg)
    await db.flush()
    return {"success": True, "data": TicketResponse.model_validate(ticket)}


@router.get("/")
async def list_tickets(page: int = Query(1, ge=1), per_page: int = Query(20, ge=1, le=50),
                       db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    total = (await db.execute(select(func.count(Ticket.id)).where(Ticket.user_id == current_user.id))).scalar_one()
    items = (await db.execute(
        select(Ticket).where(Ticket.user_id == current_user.id)
        .options(selectinload(Ticket.messages))
        .order_by(Ticket.created_at.desc()).offset((page-1)*per_page).limit(per_page)
    )).scalars().all()
    import math
    return {"success": True, "data": {
        "items": [TicketResponse.model_validate(t) for t in items],
        "total": total, "page": page, "pages": math.ceil(total/per_page) if total else 0
    }}


@router.post("/{ticket_id}/reply")
async def reply_to_ticket(ticket_id: uuid.UUID, body: str, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_active_user)):
    result = await db.execute(select(Ticket).where(Ticket.id == ticket_id, Ticket.user_id == current_user.id))
    ticket = result.scalar_one_or_none()
    if not ticket:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Ticket not found")
    msg = TicketMessage(ticket_id=ticket.id, sender_type="user", sender_id=current_user.id, body=body)
    db.add(msg)
    ticket.status = TicketStatus.IN_PROGRESS
    await db.flush()
    return {"success": True, "message": "Reply sent"}
