"""Wallet and Transaction schemas."""
import uuid
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel


class WalletResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    account_number: str
    balance: Decimal
    currency: str
    status: str
    daily_limit: Decimal
    monthly_limit: Decimal
    created_at: datetime


class TransactionResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    reference_number: str
    type: str
    status: str
    amount: Decimal
    fee: Decimal
    currency: str
    balance_before: Decimal
    balance_after: Decimal
    description: str | None
    created_at: datetime


class PaginatedTransactions(BaseModel):
    items: list[TransactionResponse]
    total: int
    page: int
    per_page: int
    pages: int
