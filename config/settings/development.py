# config/development.py

from .base import *

DEBUG = True

# for development, we don't need password validation
AUTH_PASSWORD_VALIDATORS = []


# Postgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST', 'localhost'),
        'PORT': config('DB_PORT'),
    }
}

POSTGRES_DATABASE_URL = config('DATABASE_URL')
