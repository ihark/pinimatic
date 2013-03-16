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
    HOST = 'localhost'
    SITE_IP = 'localhost'

#must run server with this port ie: python manage.py runserver 0.0.0.0:5000
#forman start uses 5000 by default.
SITE_PORT = ':5000'
SITE_URL = 'http://'+SITE_IP+SITE_PORT
'''STATIC_PREFIX
Static url can not be full url on local dev server so 
this adds it to the bookmarklet. MUST BE = '' on production.
'''
STATIC_PREFIX = SITE_URL

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
SEND_TEST_EMAIL = False

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = os.path.join(SITE_ROOT, 'media/')
MEDIA_URL = SITE_URL+'/media/'
TMP_ROOT = os.path.join(SITE_ROOT, 'media/tmp/')
TMP_URL = SITE_URL+'/media/tmp/'
STATIC_ROOT = os.path.join(SITE_ROOT, 'static/')
STATIC_URL = '/static/'
#Uplaoded images path
IMAGES_PATH = 'pins/pin/originals/'

ROOT_URLCONF = 'pinry.urls'

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'
DEFAULT_USER_GROUP = 'Basic'

INTERNAL_IPS = ['127.0.0.1']

#ALLAUTH
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = LOGIN_URL
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/user/all/'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_PASSWORD_MIN_LENGTH =6

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
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
) 

COMPRESS_CSS_FILTERS = ['compressor.filters.cssmin.CSSMinFilter']



AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",

    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
)

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
    'pinry.allauthtemplates',
    'storages',
    'follow',
    'gunicorn',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    # ... include social providers you want to enable:
    'allauth.socialaccount.providers.facebook',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.linkedin',
    #'allauth.socialaccount.providers.twitter',
)
SOCIALACCOUNT_PROVIDERS ={ 
    'facebook':
        { 'SCOPE': ['email', 'publish_stream'],
          'AUTH_PARAMS': { 'auth_type': 'reauthenticate' },
          'METHOD': 'js_sdk'},
    'linkedin':
        { 'SCOPE': ['r_emailaddress'] }
    }

