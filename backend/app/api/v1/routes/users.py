"""Users routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserResponse, UserUpdate, PasswordChange
from app.dependencies.auth import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_active_user)):
    return {"success": True, "data": UserResponse.model_validate(current_user)}


@router.patch("/me")
async def update_me(data: UserUpdate, db: AsyncSession = Depends(get_db),
                    current_user: User = Depends(get_current_active_user)):
    from app.repositories.user import UserRepository
    updated = await UserRepository(db).update(current_user.id, **data.model_dump(exclude_none=True))
    return {"success": True, "data": UserResponse.model_validate(updated)}


@router.post("/me/change-password")
async def change_password(data: PasswordChange, db: AsyncSession = Depends(get_db),
                          current_user: User = Depends(get_current_active_user)):
    from app.security.password import verify_password, hash_password
    from app.repositories.user import UserRepository
    from app.core.errors import UnauthorizedError
    if not verify_password(data.current_password, current_user.hashed_password):
        raise UnauthorizedError("Current password is incorrect")
    await UserRepository(db).update(current_user.id, hashed_password=hash_password(data.new_password))
    return {"success": True, "message": "Password changed successfully"}
