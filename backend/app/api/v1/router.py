"""Main API v1 router."""
from fastapi import APIRouter
from app.api.v1.routes import auth, users, kyc, wallet, tickets, notifications, referrals, admin, analytics

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(kyc.router)
api_router.include_router(wallet.router)
api_router.include_router(tickets.router)
api_router.include_router(notifications.router)
api_router.include_router(referrals.router)
api_router.include_router(admin.router)
api_router.include_router(analytics.router)
