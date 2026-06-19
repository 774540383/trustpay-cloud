"""Auth routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.user import UserRegister, UserLogin, UserResponse, RefreshTokenRequest
from app.services.auth_service import AuthService
from app.security.jwt import verify_refresh_token, create_access_token
from app.core.config import settings
from fastapi import HTTPException

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user, tokens = await service.register(data)
    return {"success": True, "data": {"user": UserResponse.model_validate(user), "tokens": tokens}}


@router.post("/login")
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user, tokens = await service.login(data)
    return {"success": True, "data": {"user": UserResponse.model_validate(user), "tokens": tokens}}


@router.post("/refresh")
async def refresh_token(data: RefreshTokenRequest):
    user_id = verify_refresh_token(data.refresh_token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    access_token = create_access_token(user_id)
    return {"success": True, "data": {"access_token": access_token, "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60}}


@router.post("/logout")
async def logout():
    return {"success": True, "message": "Logged out successfully"}
