#manage.py uses RACK_ENV to determine the settings file to use
from pinry.settings import *
import os

print '--Production Settings Loading'

ALLOW_NEW_REGISTRATIONS = False

#HEROKU
DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': os.environ.get("DB_NAME"),
    'HOST': 'ec2-54-243-243-204.compute-1.amazonaws.com',
    'PORT': 5432,
    'USER': os.environ.get("DB_USER"),
    'PASSWORD': os.environ.get("DB_PASSWORD"),
  }
}
SEND_TEST_EMAIL = True

SECRET_KEY = os.environ.get('SECRET_KEY')

#Set SITE_PORT='' when port is :80
SITE_PORT = ''
SITE_URL = 'http://'+SITE_IP+SITE_PORT

HOST_NAME = os.environ.get('HOST_NAME')
print 'HOST_NAME: ', HOST_NAME
print 'DB_NAME: ', os.environ.get("DB_NAME")

DEFAULT_FILE_STORAGE = 'pinry.settings.s3utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'pinry.settings.s3utils.StaticRootS3BotoStorage'
#STATICFILES_STORAGE = 'pinry.settings.s3utils.CachedS3BotoStorage'

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
print 'AWS_STORAGE_BUCKET_NAME: ', AWS_STORAGE_BUCKET_NAME
S3_URL = 'http://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME

MEDIA_URL = S3_URL+'media/'
MEDIA_ROOT = S3_URL+'media/'
STATIC_URL = S3_URL+'static/'
STATIC_ROOT = S3_URL+'static/'
TMP_ROOT = os.path.join(SITE_ROOT, 'media/tmp/')
TMP_URL = 'http://%s/media/tmp/' % HOST_NAME
'''STATIC_PREFIX
Static url can not be full url on local dev server so STATIC_PREFIX 
adds URL prefix to the bookmarklet. MUST BE = '' with remote static files.
'''
STATIC_PREFIX = ''

COMPRESS_ENABLED = True
COMPRESS_STORAGE = STATICFILES_STORAGE 
COMPRESS_URL = STATIC_URL
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_OFFLINE = False
'''COMPRESS_OFFLINE issue:
Compressing... Error: An error occured during rendering /app/pinry/pins/templates/pins/bmbase.html: '/static/vendor/boot
strap/2.0.3/css/bootstrap.css' isn't accessible via COMPRESS_URL ('http://pinry.s3.amazonaws.com/static/') and can't be
compressed
'''
