"""Authentication dependencies."""
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.security.jwt import verify_access_token
from app.repositories.user import UserRepository
from app.repositories.admin import AdminRepository
from app.models.user import User, UserStatus
from app.models.admin import Admin

bearerScheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearerScheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    repo = UserRepository(db)
    user = await repo.get_by_id(uuid.UUID(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.status == UserStatus.SUSPENDED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is suspended")
    return current_user


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearerScheme),
    db: AsyncSession = Depends(get_db),
) -> Admin:
    token = credentials.credentials
    admin_id = verify_access_token(token)
    if not admin_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    repo = AdminRepository(db)
    admin = await repo.get_by_id(uuid.UUID(admin_id))
    if not admin or not admin.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return admin


def require_permission(permission: str):
    async def checker(admin: Admin = Depends(get_current_admin)) -> Admin:
        if admin.is_super_admin:
            return admin
        if admin.role:
            perms = [p.codename for p in admin.role.permissions]
            if permission in perms:
                return admin
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Missing permission: {permission}")
    return checker
