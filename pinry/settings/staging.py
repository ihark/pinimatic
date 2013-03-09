#manage.py uses RACK_ENV to determine the settings file to use
from pinry.settings import *
from pinry.settings.production import *
import os

print '--Staging Settings Loading'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ALLOW_NEW_REGISTRATIONS = False

#HEROKU
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': os.environ.get("DB_NAME"),
    'HOST': 'ec2-23-21-170-190.compute-1.amazonaws.com',
    'PORT': 5432,
    'USER': os.environ.get("DB_USER"),
    'PASSWORD': os.environ.get("DB_PASSWORD"),
  }
}
