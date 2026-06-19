"""Referral schemas."""
import uuid
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel


class ReferralResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    referred_id: uuid.UUID
    status: str
    reward_amount: Decimal
    reward_points: int
    reward_paid: bool
    created_at: datetime
