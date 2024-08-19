# config/development.py

from .base import *

DEBUG = True

# for development, we don't need password validation
AUTH_PASSWORD_VALIDATORS = []
