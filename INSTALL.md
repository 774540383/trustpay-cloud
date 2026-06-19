# دليل التثبيت - TrustPay

## المتطلبات

- Docker >= 24.0
- Docker Compose >= 2.20
- Python >= 3.12 (للتطوير المحلي)
- Node.js >= 20 (للـ frontend)

## التثبيت باستخدام Docker (موصى به)

```bash
# 1. انسخ المستودع
git clone https://github.com/774540383/trustpay-cloud.git
cd trustpay-cloud

# 2. اضبط متغيرات البيئة
cp backend/.env.example backend/.env
# عدّل backend/.env بقيم حقيقية

# 3. شغّل الخدمات
docker compose up -d

# 4. تحقق من الصحة
curl http://localhost:8000/health
```

## التطوير المحلي (بدون Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# شغّل قاعدة البيانات و Redis منفصلاً
docker compose up postgres redis -d

# نفّذ migrations
alembic upgrade head

# أضف بيانات أولية
python scripts/seed.py

# شغّل الـ API
uvicorn app.main:app --reload --port 8000
```

## الوصول

| الخدمة | الرابط |
|--------|--------|
| API Docs | http://localhost:8000/docs |
| API ReDoc | http://localhost:8000/redoc |
| Health | http://localhost:8000/health |
