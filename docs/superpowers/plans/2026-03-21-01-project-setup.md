# Project Setup & Configuration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up Django project structure, split settings into environments, install dependencies, and create the budget app.

**Architecture:** Django monolithic app with settings split (base/development/production), SQLite for dev.

**Tech Stack:** Django 6.0, Python 3.11+, pytest for testing

---

## Task 1: Split Django Settings into Environments

**Files:**
- Create: `core/settings/__init__.py`
- Create: `core/settings/base.py`
- Create: `core/settings/development.py`
- Create: `core/settings/production.py`
- Modify: `core/settings.py` (will be deleted after split)

- [x] **Step 1: Create settings directory structure**

```bash
mkdir core/settings
touch core/settings/__init__.py
```

- [x] **Step 2: Move base settings to base.py**

Create `core/settings/base.py` with common settings (from current settings.py):

```python
"""
Base settings for budget-control project.
Settings common to all environments.
"""
from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-93vs8%!t1kn9+_mgvg4!&+3m3pixb)&n%91fhcvk4hbr!63!oo')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
```

- [x] **Step 3: Create development settings**

Create `core/settings/development.py`:

```python
"""
Development-specific settings.
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Development-only apps
INSTALLED_APPS += [
    'django_extensions',  # Optional: useful dev tools
]
```

- [x] **Step 4: Create production settings**

Create `core/settings/production.py`:

```python
"""
Production-specific settings.
"""
from .base import *
import os

DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database - PostgreSQL for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

- [x] **Step 5: Update settings/__init__.py to auto-load environment**

Create `core/settings/__init__.py`:

```python
"""
Settings module that auto-loads the correct environment.
"""
import os

ENVIRONMENT = os.environ.get('DJANGO_ENV', 'development')

if ENVIRONMENT == 'production':
    from .production import *
else:
    from .development import *
```

- [x] **Step 6: Delete old settings.py file**

```bash
rm core/settings.py
```

- [x] **Step 7: Test settings import**

```bash
python manage.py check
```

Expected: No errors, system check passes

- [x] **Step 8: Commit settings reorganization**

```bash
git add core/settings/
git rm core/settings.py
git commit -m "refactor: split settings into base/dev/prod environments"
```

---

## Task 2: Update Requirements and Install Dependencies

**Files:**
- Modify: `requirements.txt`
- Create: `requirements/base.txt`
- Create: `requirements/development.txt`
- Create: `requirements/production.txt`

- [ ] **Step 1: Create requirements directory**

```bash
mkdir requirements
```

- [ ] **Step 2: Create base requirements**

Create `requirements/base.txt`:

```
django==6.0.3
pillow==11.0.0
python-decouple==3.8
google-api-python-client==2.151.0
google-auth-httplib2==0.2.0
google-auth-oauthlib==1.2.1
requests==2.32.3
```

- [ ] **Step 3: Create development requirements**

Create `requirements/development.txt`:

```
-r base.txt

pytest==8.3.4
pytest-django==4.9.0
pytest-cov==6.0.0
django-extensions==3.2.3
ipython==8.31.0
```

- [ ] **Step 4: Create production requirements**

Create `requirements/production.txt`:

```
-r base.txt

psycopg2-binary==2.9.10
gunicorn==23.0.0
whitenoise==6.8.2
```

- [ ] **Step 5: Update root requirements.txt**

Update `requirements.txt`:

```
# Development requirements by default
-r requirements/development.txt
```

- [ ] **Step 6: Install development dependencies**

```bash
pip install -r requirements.txt
```

Expected: All packages install successfully

- [ ] **Step 7: Commit requirements update**

```bash
git add requirements/ requirements.txt
git commit -m "feat: add comprehensive project dependencies"
```

---

## Task 3: Create Budget Django App

**Files:**
- Create: `budget/` (entire app structure)

- [ ] **Step 1: Create budget app**

```bash
python manage.py startapp budget
```

- [ ] **Step 2: Create models directory structure**

```bash
mkdir budget/models
touch budget/models/__init__.py
touch budget/models/user.py
touch budget/models/unit.py
touch budget/models/receipt.py
```

- [ ] **Step 3: Create views directory structure**

```bash
mkdir budget/views
touch budget/views/__init__.py
touch budget/views/auth.py
touch budget/views/dashboard.py
touch budget/views/receipts.py
touch budget/views/review.py
touch budget/views/management.py
```

- [ ] **Step 4: Create forms directory structure**

```bash
mkdir budget/forms
touch budget/forms/__init__.py
touch budget/forms/auth_forms.py
touch budget/forms/receipt_forms.py
touch budget/forms/management_forms.py
```

- [ ] **Step 5: Create services directory structure**

```bash
mkdir budget/services
touch budget/services/__init__.py
touch budget/services/ocr_service.py
touch budget/services/storage_service.py
```

- [ ] **Step 6: Create templates directory structure**

```bash
mkdir -p budget/templates/budget/auth
mkdir -p budget/templates/budget/dashboard
mkdir -p budget/templates/budget/receipts
mkdir -p budget/templates/budget/review
mkdir -p budget/templates/budget/management
```

- [ ] **Step 7: Create static directory structure**

```bash
mkdir -p budget/static/budget/css
mkdir -p budget/static/budget/js
```

- [ ] **Step 8: Create tests directory structure**

```bash
mkdir budget/tests
touch budget/tests/__init__.py
touch budget/tests/test_models.py
touch budget/tests/test_views.py
touch budget/tests/test_services.py
touch budget/tests/test_forms.py
```

- [ ] **Step 9: Add budget app to INSTALLED_APPS**

Edit `core/settings/base.py`, add to INSTALLED_APPS:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'budget',  # Add this line
]
```

- [ ] **Step 10: Test app detection**

```bash
python manage.py check
```

Expected: No errors

- [ ] **Step 11: Commit budget app creation**

```bash
git add budget/ core/settings/base.py
git commit -m "feat: create budget Django app with directory structure"
```

---

## Task 4: Configure Testing Framework

**Files:**
- Create: `pytest.ini`
- Create: `.coveragerc`

- [ ] **Step 1: Create pytest configuration**

Create `pytest.ini`:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = core.settings
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --strict-markers
    --tb=short
    --cov=budget
    --cov-report=term-missing
    --cov-report=html
testpaths = budget/tests
```

- [ ] **Step 2: Create coverage configuration**

Create `.coveragerc`:

```ini
[run]
source = budget
omit = 
    */migrations/*
    */tests/*
    */__init__.py
    */admin.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

- [ ] **Step 3: Create initial test to verify setup**

Edit `budget/tests/test_models.py`:

```python
"""
Test suite for budget app models.
"""
import pytest
from django.test import TestCase


class TestProjectSetup(TestCase):
    """Verify project setup is working."""
    
    def test_django_environment(self):
        """Test that Django test environment is configured."""
        assert True
```

- [ ] **Step 4: Run initial test**

```bash
pytest
```

Expected: 1 test passes

- [ ] **Step 5: Commit testing configuration**

```bash
git add pytest.ini .coveragerc budget/tests/test_models.py
git commit -m "feat: configure pytest and coverage for testing"
```

---

## Task 5: Create Environment Variables Template

**Files:**
- Create: `.env.example`
- Create: `.env` (git-ignored)

- [ ] **Step 1: Create .env.example template**

Create `.env.example`:

```env
# Django Configuration
DJANGO_ENV=development
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (Production)
DB_NAME=budget_control
DB_USER=postgres
DB_PASSWORD=your-password-here
DB_HOST=localhost
DB_PORT=5432

# OCR Provider (gemini or openrouter)
OCR_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-api-key
OPENROUTER_API_KEY=your-openrouter-api-key

# Storage Provider (google_drive or cloudinary)
STORAGE_PROVIDER=google_drive
GOOGLE_DRIVE_CREDENTIALS_FILE=path/to/credentials.json
CLOUDINARY_URL=cloudinary://your-cloudinary-url

# Allowed Hosts (comma-separated for production)
ALLOWED_HOSTS=localhost,127.0.0.1
```

- [ ] **Step 2: Create local .env file**

```bash
cp .env.example .env
```

- [ ] **Step 3: Ensure .env is in .gitignore**

Verify `.gitignore` contains:

```
.env
*.pyc
__pycache__/
db.sqlite3
media/
staticfiles/
htmlcov/
.coverage
*.log
```

- [ ] **Step 4: Test environment loading**

```bash
python manage.py check
```

Expected: No errors

- [ ] **Step 5: Commit environment template**

```bash
git add .env.example .gitignore
git commit -m "feat: add environment variables template"
```

---

## Task 6: Create Initial Database Migration

**Files:**
- Create: `budget/migrations/0001_initial.py` (auto-generated)

- [ ] **Step 1: Create initial migrations**

```bash
python manage.py makemigrations
```

Expected: No changes detected (no models yet)

- [ ] **Step 2: Run migrations**

```bash
python manage.py migrate
```

Expected: All Django default migrations apply successfully

- [ ] **Step 3: Create superuser for admin access**

```bash
python manage.py createsuperuser
```

Enter credentials when prompted:
- Username: admin
- Email: admin@example.com
- Password: (choose secure password)

- [ ] **Step 4: Test development server**

```bash
python manage.py runserver
```

Expected: Server starts on http://127.0.0.1:8000/

- [ ] **Step 5: Test admin access**

Navigate to http://127.0.0.1:8000/admin/
Expected: Admin login page loads

- [ ] **Step 6: Stop server and commit**

Press Ctrl+C to stop server

```bash
git add .
git commit -m "feat: run initial migrations and verify project setup"
```

---

## Completion Checklist

After completing all tasks:

- [x] Settings split into base/development/production
- [x] Dependencies installed and requirements organized
- [x] Budget app created with proper directory structure
- [x] Testing framework configured (pytest + coverage)
- [x] Environment variables template created
- [x] Initial migrations run successfully
- [x] Development server runs without errors
- [x] Admin interface accessible

**Next Plan:** 2026-03-21-02-authentication-user-management.md
