"""Admin repository."""
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.admin import Admin


class AdminRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, admin_id: uuid.UUID) -> Admin | None:
        result = await self.db.execute(select(Admin).where(Admin.id == admin_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Admin | None:
        result = await self.db.execute(select(Admin).where(Admin.email == email))
        return result.scalar_one_or_none()
