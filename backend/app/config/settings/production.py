import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *

DEBUG = False

ENV = 'Production'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += []

MIDDLEWARE = [
    # django-cors-header
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # whitenoise for production
    'whitenoise.middleware.WhiteNoiseMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

WSGI_APPLICATION = 'config.wsgi.production.application'

# Sentry setting
sentry_sdk.init(
    dsn=config('SENTRY_DSN'),
    integrations=[DjangoIntegration()],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True
)