from .base import *

DEBUG = False

ENV = 'Production'

ALLOWED_HOSTS = ['*']

INSTALLED_APPS += []

WSGI_APPLICATION = 'config.wsgi.production.application'
