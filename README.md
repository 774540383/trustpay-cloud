# TrustPay 🏦

منصة Fintech رقمية متكاملة لإدارة العملاء، التحقق من الهوية (KYC)، المحافظ، التذاكر، الإحالات، والإشعارات.

## المكونات

| المكوِّن | التقنية | الوصف |
|---------|---------|-------|
| Backend | FastAPI + PostgreSQL + Redis | API رئيسي |
| Frontend | Next.js + TypeScript + Tailwind | واجهة الويب |
| Bot الرئيسي | Aiogram | بوت تيليجرام الرئيسي |
| Bot KYC | Aiogram | بوت التحقق من الهوية |
| Admin Panel | Next.js | لوحة الإدارة |

## تشغيل سريع

```bash
git clone https://github.com/774540383/trustpay-cloud.git
cd trustpay-cloud
cp backend/.env.example backend/.env
# عدّل .env بإعداداتك
docker compose up -d
```

الـ API متاح على: http://localhost:8000/docs

## الهيكل

```
trustpay-cloud/
├── backend/          # FastAPI
├── frontend/         # Next.js
├── telegram-main-bot/
├── telegram-kyc-bot/
├── admin-panel/
├── docs/
└── infrastructure/
```

## المراحل

- [x] المرحلة 1: Backend كامل
- [ ] المرحلة 2: Frontend (Next.js)
- [ ] المرحلة 3: Telegram Bots
- [ ] المرحلة 4: Admin Panel
- [ ] المرحلة 5: Infrastructure & Deployment
