#manage.py uses RACK_ENV to determine the settings file to use
#from pinry.settings.settings import *
from pinry.settings import *
import os

print '--Development Settings Loading'

DEBUG = True
TEMPLATE_DEBUG = DEBUG
PUBLIC = False

#HTTPS
HTTPS_SUPPORT = True
LOGIN_REDIRECT_URL = SITE_URL+LOGIN_REDIRECT_URL

'''
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(SITE_ROOT, 'development.db'),
  }
}
'''
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'pinimatic',
    'HOST': 'localhost',
    'PORT': 5432,
    'USER': 'postgres',
    'PASSWORD': os.environ.get("DB_PASSWORD"),
  }
}


SECRET_KEY = 'fake-key'