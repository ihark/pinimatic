#manage.py uses RACK_ENV to determine the settings file to use
from pinry.settings import *

import os

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
#import dj_database_url
#DATABASES = {'default': dj_database_url.config(default=os.environ['DATABASE_URL'])

#from storages.backends.s3boto import S3BotoStorage
#StaticS3BotoStorage = lambda: S3BotoStorage(location='static')
#MediaS3BotoStorage = lambda: S3BotoStorage(location='media')


DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
STATICFILES_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
#from S3 import CallingFormat
#AWS_CALLING_FORMAT = CallingFormat.SUBDOMAIN
S3_URL = 'http://s3.amazonaws.com/%s/' % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = S3_URL
MEDIA_ROOT = S3_URL
TMP_ROOT = os.path.join(SITE_ROOT, 'media/tmp/')
TMP_URL = 'http://pinry.herokuapp.com/media/tmp/'
#STATIC_URL = S3_URL

# TODO: Be sure to set this.
SECRET_KEY = os.environ.get('S3_BUCKET_NAME')

