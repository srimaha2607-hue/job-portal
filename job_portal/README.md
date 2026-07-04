# Job Portal — Django Full-Stack Application

## Quick Start

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Create admin user
python manage.py createsuperuser

# 5. (Optional) Load demo categories
python manage.py loaddata fixtures/categories.json

# 6. Start dev server
python manage.py runserver
```

Open http://127.0.0.1:8000

## User Roles
- **Admin**: Full control — visit /admin/
- **Recruiter**: Post & manage jobs, review applicants
- **Job Seeker**: Browse, apply, save jobs, upload resume

## 2FA Setup
1. Register or log in
2. Go to Profile → Enable 2FA
3. Scan QR with Google Authenticator / Authy
4. Enter 6-digit OTP to confirm
5. Save recovery codes safely

## Key URLs
| Page | URL |
|------|-----|
| Home | / |
| Jobs | /jobs/ |
| Register | /accounts/register/ |
| Login | /accounts/login/ |
| Dashboard | /dashboard/ |
| Profile | /accounts/profile/ |
| 2FA Setup | /accounts/2fa/setup/ |
| Admin | /admin/ |

## Tech Stack
- Django 4.2, Python 3.10+
- Bootstrap 5, Chart.js
- pyotp + qrcode (TOTP 2FA)
- django-axes (rate limiting)
- SQLite (dev) / PostgreSQL (prod)
- WhiteNoise (static files)
