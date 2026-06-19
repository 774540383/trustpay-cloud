"""User repository."""
import uuid
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, **kwargs) -> User:
        user = User(**kwargs)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_referral_code(self, code: str) -> User | None:
        result = await self.db.execute(select(User).where(User.referral_code == code))
        return result.scalar_one_or_none()

    async def get_by_telegram_id(self, telegram_id: str) -> User | None:
        result = await self.db.execute(select(User).where(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()

    async def exists_email(self, email: str) -> bool:
        count = await self.db.execute(
            select(func.count(User.id)).where(User.email == email)
        )
        return count.scalar_one() > 0

    async def update(self, user_id: uuid.UUID, **kwargs) -> User:
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one()
        for key, value in kwargs.items():
            setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def list_all(
        self, offset: int = 0, limit: int = 20, status: str | None = None
    ) -> tuple[list[User], int]:
        q = select(User)
        if status:
            q = q.where(User.status == status)
        total_result = await self.db.execute(select(func.count(User.id)))
        total = total_result.scalar_one()
        users_result = await self.db.execute(q.order_by(User.created_at.desc()).offset(offset).limit(limit))
        return list(users_result.scalars().all()), total
