#manage.py uses RACK_ENV to determine the settings file to use
#from pinry.settings.settings import *
from pinry.settings import *
from pinry.settings.env import *
import os

print '--Development Settings Loading'

# quick toggles to overide init
DEBUG = True
PUBLIC = True
COMPRESS_ENABLED = False
#use in templates that to dont get context processors to prfix statc path on development server

EMAIL_STATIC_HOST_PORT = HTTP_DEV_PORT
# SQLite3
'''
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.sqlite3',
    'NAME': os.path.join(SITE_ROOT, 'development.db'),
  }
}
'''
# Heroku postgreSQL
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