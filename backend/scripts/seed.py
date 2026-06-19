"""Seed initial data into TrustPay database."""
import asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from app.models.role import Role
from app.models.admin import Admin
from app.models.loyalty_level import LoyaltyLevel
from app.security.password import hash_password


async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as db:
        # Roles
        roles_data = [
            {"name": "Super Admin", "codename": "super_admin", "is_system": True},
            {"name": "Admin", "codename": "admin", "is_system": True},
            {"name": "Reviewer", "codename": "reviewer", "is_system": True},
            {"name": "Support Agent", "codename": "support_agent", "is_system": True},
        ]
        roles = {}
        for rd in roles_data:
            role = Role(**rd)
            db.add(role)
            await db.flush()
            roles[rd["codename"]] = role

        # Super Admin
        admin = Admin(
            email=settings.ADMIN_EMAIL,
            full_name="Super Admin",
            hashed_password=hash_password(settings.ADMIN_PASSWORD),
            is_super_admin=True,
            role_id=roles["super_admin"].id,
        )
        db.add(admin)

        # Loyalty Levels
        levels = [
            {"name": "Bronze", "name_ar": "\u0628\u0631\u0648\u0646\u0632\u064a", "level_order": 1, "min_points": 0, "max_points": 999, "color": "#CD7F32", "cashback_rate": "0.005"},
            {"name": "Silver", "name_ar": "\u0641\u0636\u064a", "level_order": 2, "min_points": 1000, "max_points": 4999, "color": "#C0C0C0", "cashback_rate": "0.01"},
            {"name": "Gold", "name_ar": "\u0630\u0647\u0628\u064a", "level_order": 3, "min_points": 5000, "max_points": 19999, "color": "#FFD700", "cashback_rate": "0.015"},
            {"name": "VIP", "name_ar": "VIP", "level_order": 4, "min_points": 20000, "max_points": None, "color": "#8B008B", "cashback_rate": "0.02"},
        ]
        for lvl in levels:
            ll = LoyaltyLevel(
                name=lvl["name"], name_ar=lvl["name_ar"],
                level_order=lvl["level_order"], min_points=lvl["min_points"],
                max_points=lvl["max_points"], color=lvl["color"],
                cashback_rate=Decimal(lvl["cashback_rate"]),
            )
            db.add(ll)

        await db.commit()
        print("\u2705 Seed data inserted successfully!")
        print(f"\u2705 Admin login: {settings.ADMIN_EMAIL} / {settings.ADMIN_PASSWORD}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
