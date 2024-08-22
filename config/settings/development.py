# config/development.py

import dj_database_url
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# for development, we don't need password validation
AUTH_PASSWORD_VALIDATORS = []


# Postgres
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME'),
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST', 'localhost'),
#         'PORT': config('DB_PORT'),
#     }
# }

POSTGRES_CONNECTION_STRING = config('DATABASE_URL')
DATABASES = {
    'default': dj_database_url.parse(POSTGRES_CONNECTION_STRING)
}
