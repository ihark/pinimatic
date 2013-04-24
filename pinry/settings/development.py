#manage.py uses RACK_ENV to determine the settings file to use
#from pinry.settings.settings import *
from pinry.settings import *
from pinry.settings.env import *
import os

print '--Development Settings Loading'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
PUBLIC = False

#HTTPS
HTTPS_SUPPORT = True
LOGIN_REDIRECT_URL = SITE_URL+LOGIN_REDIRECT_URL

#COMPRESSOR
COMPRESS_ENABLED = True
#COMPRESS_STORAGE = STATICFILES_STORAGE 
COMPRESS_URL = STATIC_URL
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_OFFLINE = False

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
    'PASSWORD': DB_PASSWORD,
  }
}


SECRET_KEY = 'fake-key'