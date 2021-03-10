from .base import *

DEBUG = True

ENV = 'Dev'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += []

WSGI_APPLICATION = 'config.wsgi.dev.application'
