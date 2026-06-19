"""User schemas (Pydantic v2)."""
import uuid
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.security.password import validate_password_strength


class UserRegister(BaseModel):
    email: EmailStr
    phone: str | None = None
    password: str = Field(min_length=8)
    referral_code: str | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not validate_password_strength(v):
            raise ValueError(
                "Password must be at least 8 chars, contain uppercase, lowercase, digit, and special character."
            )
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    phone: str | None = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not validate_password_strength(v):
            raise ValueError("Weak password")
        return v


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    email: str
    phone: str | None
    status: str
    role: str
    kyc_status: str
    referral_code: str | None
    is_email_verified: bool
    is_phone_verified: bool
    loyalty_points: int
    created_at: datetime
    last_login_at: datetime | None
