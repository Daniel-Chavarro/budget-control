"""
Production-specific settings.
"""
from .base import *
import os
from django.core.exceptions import ImproperlyConfigured

DEBUG = False

# Validate SECRET_KEY
SECRET_KEY = os.environ.get('SECRET_KEY', '')
if not SECRET_KEY:
    raise ImproperlyConfigured(
        "SECRET_KEY environment variable is required in production but is missing or empty."
    )

# Validate ALLOWED_HOSTS
ALLOWED_HOSTS = [
    host.strip() for host in os.environ.get('ALLOWED_HOSTS', '').split(',')
    if host.strip()
]
if not ALLOWED_HOSTS:
    raise ImproperlyConfigured(
        "ALLOWED_HOSTS environment variable is required in production but is missing or empty."
    )

# Validate database configuration
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')

missing_db_vars = []
if not DB_NAME:
    missing_db_vars.append('DB_NAME')
if not DB_USER:
    missing_db_vars.append('DB_USER')
if not DB_PASSWORD:
    missing_db_vars.append('DB_PASSWORD')

if missing_db_vars:
    raise ImproperlyConfigured(
        f"Required database environment variables are missing or empty: {', '.join(missing_db_vars)}"
    )

# Database - PostgreSQL for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'CONN_MAX_AGE': int(os.environ.get('DB_CONN_MAX_AGE', 0)),
    }
}

# Security settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True