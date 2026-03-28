"""
Settings module that autoloads the correct environment.
"""
import os

ENVIRONMENT = os.environ.get('DJANGO_ENV', 'development')

if ENVIRONMENT == 'production':
    from .production import *
elif ENVIRONMENT == 'development':
    from .development import *
else:
    raise RuntimeError(
        f"Invalid DJANGO_ENV value: '{ENVIRONMENT}'. "
        f"Allowed values are: 'development', 'production'"
    )