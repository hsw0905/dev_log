from .base import *

ENV = 'dev_test'

TEST = True

WSGI_APPLICATION = 'config.wsgi.dev.application'

DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]