from email.policy import default
from .local import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# postgres
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}