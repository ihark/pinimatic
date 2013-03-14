import os
import socket
from django.contrib.messages import constants as messages


print '--General Settings Loading'

SITE_ID = 1
SITE_ROOT = os.path.join(os.path.realpath(os.path.dirname(__file__)), '../../')

import socket
try:
    HOST = socket.gethostname()#not used
    SITE_IP = socket.gethostbyname(socket.gethostname())
except:
    HOST = 'localhost:8000'
    SITE_IP = 'localhost:8000'

print 'SITE_IP = '+str(SITE_IP)
print 'HOST = '+str(HOST)

# Changes the naming on the front-end of the website.
SITE_NAME = 'Pinimatic'
# Set to False to disable people from creating new accounts.
ALLOW_NEW_REGISTRATIONS = True
# Set to False to force users to login before seeing any pins. 
PUBLIC = True

# Set up email
EMAIL_USE_TLS = True
EMAIL_PORT = '587'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

# Set ture to send a start up email to admins.
SEND_TEST_EMAIL = True

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = os.path.join(SITE_ROOT, 'media/')
MEDIA_URL = 'http://'+SITE_IP+':8000/media/'
TMP_ROOT = os.path.join(SITE_ROOT, 'media/tmp/')
TMP_URL = 'http://'+SITE_IP+':8000/media/tmp/'
STATIC_ROOT = os.path.join(SITE_ROOT, 'static/')
STATIC_URL = '/static/'
IMAGES_PATH = 'pins/pin/originals/'
'''STATIC_PREFIX
Static url can not be full url on local dev server so 
this adds it to the bookmarklet. MUST BE = '' on production.
'''
STATIC_PREFIX = 'http://'+SITE_IP+':8000'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.auth.middleware.RemoteUserMiddleware',
    'pinry.core.middleware.CustomHeaderMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'pinry.core.middleware.Public',
    'pinry.core.middleware.AllowOriginMiddleware', 
    'pinry.core.middleware.AjaxMessaging',
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.request",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "pinry.core.context_processors.template_settings",
    "pinry.core.context_processors.baseUrl",
    "pinry.core.context_processors.staticPrefix",
) 

COMPRESS_CSS_FILTERS = ['compressor.filters.cssmin.CSSMinFilter']

ROOT_URLCONF = 'pinry.urls'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'
DEFAULT_USER_GROUP = 'Basic'

INTERNAL_IPS = ['127.0.0.1']

MESSAGE_TAGS = {
    messages.WARNING: 'alert',
    messages.ERROR: 'alert alert-error',
    messages.SUCCESS: 'alert alert-success',
    messages.INFO: 'alert alert-info',
}
API_LIMIT_PER_PAGE = 30

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.comments',
    'south',
    'compressor',
    'taggit',
    'pinry.vendor',
    'pinry.core',
    'pinry.pins',
    'pinry.api',
    'pinry.bookmarklet',
    'storages',
    'follow',
)

