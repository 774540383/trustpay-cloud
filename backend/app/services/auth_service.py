"""Authentication service."""
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.security.jwt import create_access_token, create_refresh_token
from app.security.password import hash_password, verify_password
from app.schemas.user import UserRegister, UserLogin, TokenResponse
from app.models.user import User, UserStatus
from app.core.errors import ConflictError, UnauthorizedError
import random, string


def generate_referral_code(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, data: UserRegister) -> tuple[User, TokenResponse]:
        if await self.user_repo.exists_email(data.email):
            raise ConflictError("Email already registered")

        referred_by_id = None
        if data.referral_code:
            referrer = await self.user_repo.get_by_referral_code(data.referral_code)
            if referrer:
                referred_by_id = referrer.id

        code = generate_referral_code()
        while await self.user_repo.get_by_referral_code(code):
            code = generate_referral_code()

        user = await self.user_repo.create(
            email=data.email,
            phone=data.phone,
            hashed_password=hash_password(data.password),
            referral_code=code,
            referred_by_id=referred_by_id,
            status=UserStatus.PENDING_VERIFICATION,
        )

        from app.models.wallet import Wallet
        acct = f"TP{random.randint(10000000, 99999999)}"
        wallet = Wallet(user_id=user.id, account_number=acct)
        self.db.add(wallet)
        await self.db.flush()

        return user, self._create_tokens(user)

    async def login(self, data: UserLogin) -> tuple[User, TokenResponse]:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not user.hashed_password:
            raise UnauthorizedError("Invalid credentials")
        if not verify_password(data.password, user.hashed_password):
            await self.user_repo.update(user.id, failed_login_attempts=user.failed_login_attempts + 1)
            raise UnauthorizedError("Invalid credentials")
        now = datetime.now(timezone.utc)
        await self.user_repo.update(
            user.id, last_login_at=now,
            login_count=user.login_count + 1, failed_login_attempts=0,
        )
        return user, self._create_tokens(user)

    def _create_tokens(self, user: User) -> TokenResponse:
        from app.core.config import settings
        access = create_access_token(str(user.id), {"role": user.role, "email": user.email})
        refresh = create_refresh_token(str(user.id))
        return TokenResponse(
            access_token=access, refresh_token=refresh,
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
