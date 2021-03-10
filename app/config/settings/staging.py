from .base import *

DEBUG = False

ENV = 'Staging'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += []

WSGI_APPLICATION = 'config.wsgi.staging.application'
