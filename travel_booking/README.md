## Travel Booking Application

This is a Django app for browsing travel options, booking seats, and managing bookings. It supports SQLite (default) or MySQL via environment variables.

### Prerequisites
- Python 3.11+ (Windows: install from Microsoft Store or python.org)
- Optional: MySQL Server + MySQL Workbench

### 1) Create virtual environment and install dependencies
Run in a terminal at the project root (`travel_booking/` contains `manage.py`). On Windows PowerShell:
```
py -3 -m venv .venv
.\.venv\Scripts\python -m pip install -U pip
.\.venv\Scripts\python -m pip install -r requirements.txt
```

If your PowerShell blocks script activation, do NOT run `Activate.ps1`. Always call Python via `.\.venv\Scripts\python` as above.

### 2) Configure environment (.env)
Create a file named `.env` in the project directory next to `manage.py` with at least:
```
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database (set USE_MYSQL=True to use MySQL; otherwise SQLite is used)
USE_MYSQL=False
MYSQL_NAME=travel_booking_db
MYSQL_USER=your_mysql_user
MYSQL_PASSWORD=your_mysql_password
MYSQL_HOST=localhost
MYSQL_PORT=3306

# Email (console by default; override for SMTP)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.example.com
# EMAIL_PORT=587
# EMAIL_HOST_USER=...
# EMAIL_HOST_PASSWORD=...
# EMAIL_USE_TLS=True
```

### 3) MySQL quick start (optional)
In MySQL Workbench, run:
```
CREATE DATABASE IF NOT EXISTS travel_booking_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'travel_user'@'localhost' IDENTIFIED BY 'StrongPassword!123';
GRANT ALL PRIVILEGES ON travel_booking_db.* TO 'travel_user'@'localhost';
FLUSH PRIVILEGES;
```
Then set in `.env`:
```
USE_MYSQL=True
MYSQL_NAME=travel_booking_db
MYSQL_USER=travel_user
MYSQL_PASSWORD=StrongPassword!123
```

### 4) Initialize database and run the app
```
.\.venv\Scripts\python manage.py makemigrations
.\.venv\Scripts\python manage.py migrate

# Load small starter fixtures
.\.venv\Scripts\python manage.py loaddata fixtures/sample_data.json

# Optionally generate many India-heavy routes (75 by default)
.\.venv\Scripts\python manage.py seed_travel_options --count 75

# Create admin user
.\.venv\Scripts\python manage.py createsuperuser

# Start server
.\.venv\Scripts\python manage.py runserver
```
Visit http://127.0.0.1:8000/

### 5) Running tests
```
.\.venv\Scripts\python manage.py test
```

### Troubleshooting
- PowerShell execution policy blocks activation: skip activation and call `.\.venv\Scripts\python` directly.
- Using MySQL but migrations still go to SQLite: ensure `.env` has `USE_MYSQL=True` and restart the server.
- Verify active DB from Django shell:
```
.\.venv\Scripts\python manage.py shell -c "from django.db import connection; print(connection.vendor, connection.settings_dict['NAME'])"
```
- If you see `ModuleNotFoundError: whitenoise`, install it:
```
.\.venv\Scripts\python -m pip install whitenoise==6.7.0
```

### Features
- User registration/login/logout and profile management
- Search/filter by type, source, destination, date
- Booking with seat validation and atomic seat updates; cancellation restores seats
- Email notifications (console by default)
- Bootstrap 5 responsive UI
- Admin panels for managing data

