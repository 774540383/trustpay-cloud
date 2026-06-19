# TrustPay - Architecture Overview

## System Design

```
┌─────────────────────────────────────────────────────┐
│                   Clients                           │
│  Web Browser │ Telegram Bot │ Telegram Mini App     │
└──────┬───────────────┬──────────────────────────────┘
       │               │
       ▼               ▼
┌─────────────────────────────────────────────────────┐
│              API Gateway / Nginx                    │
└──────────────────────┬──────────────────────────────┘
                       │
       ┌───────────────┼───────────────┐
       ▼               ▼               ▼
┌──────────┐   ┌──────────────┐  ┌──────────────┐
│ Backend  │   │   Frontend   │  │ Admin Panel  │
│ FastAPI  │   │   Next.js    │  │   Next.js    │
└────┬─────┘   └──────────────┘  └──────────────┘
     │
     ├──────────────┐
     ▼              ▼
┌──────────┐  ┌──────────┐
│PostgreSQL│  │  Redis   │
└──────────┘  └──────────┘
```

## Modules

### Backend (FastAPI)
- **Auth**: JWT tokens, refresh tokens, RBAC
- **Users**: Registration, profiles, activity logs
- **KYC**: Multi-step wizard, document upload, admin review
- **Wallet**: Balance management, transactions, ledger
- **Tickets**: Support system with attachments
- **Referrals**: Referral tree, rewards engine
- **Notifications**: Telegram, email, in-app
- **Analytics**: Metrics dashboard

### Database (PostgreSQL)
See `/docs/ERD.md` for entity relationship diagram.

### Cache (Redis)
- JWT token blacklist
- Rate limiting counters
- Session data
- Notification queues

## Security
- JWT + Refresh tokens
- RBAC (Role-Based Access Control)
- Rate limiting per IP and user
- Input validation via Pydantic
- Audit logs for all mutations
- Secrets via environment variables only
