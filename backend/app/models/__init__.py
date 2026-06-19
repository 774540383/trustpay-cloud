"""Import all models so Alembic can detect them."""
from app.models.user import User
from app.models.profile import Profile
from app.models.wallet import Wallet
from app.models.transaction import Transaction
from app.models.kyc_request import KYCRequest
from app.models.kyc_document import KYCDocument
from app.models.ticket import Ticket
from app.models.ticket_message import TicketMessage
from app.models.referral import Referral
from app.models.loyalty_level import LoyaltyLevel
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.models.admin import Admin
from app.models.role import Role, Permission, role_permissions

__all__ = [
    "User", "Profile", "Wallet", "Transaction",
    "KYCRequest", "KYCDocument", "Ticket", "TicketMessage",
    "Referral", "LoyaltyLevel", "Notification", "AuditLog",
    "Admin", "Role", "Permission", "role_permissions",
]
