import os
import socket
from django.contrib.messages import constants as messages

print '--General Settings Loading'

#SITE & HOST
SITE_ID = 1
SITE_ROOT = os.path.join(os.path.realpath(os.path.dirname(__file__)), '../../')

import socket
try:
    SITE_IP = socket.gethostbyname(socket.gethostname())
except:
    SITE_IP = 'localhost'

''' HTTPS_DEV_PORT & HTTP_DEV_PORT (required for development server only)
# You must run the development server with the ports specified below
# to handle http & https redirects. They are not needed in a production env.
# ie: python manage.py runserver 0.0.0.0:5000, forman uses 5000 by default.
# set stunnel or similar SSL proxy to handle the SSL requestes on the port specified
'''
HTTPS_DEV_PORT='5443'
HTTP_DEV_PORT = ':5000'
HOST_NAME = os.environ.get('HOST_NAME', SITE_IP)
SITE_URL = 'http://'+HOST_NAME+HTTP_DEV_PORT

# Changes the naming on the front-end of the website.
SITE_NAME = 'Pinimatic'

# Infroms javaScript of current api name.
API_NAME = 'v1'

# Set acording to your privacy policy. 
P3P_COMPACT = 'CP="NOI OUR NID PSA"'

# Set to False to force users to login before seeing any pins. 
PUBLIC = True

#LOGIN LOGOUT (keep above allauth)
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
#TODO: Not working possible version issue: ACCOUNT_LOGOUT_REDIRECT_URL ='/login/'
ALLOW_NEW_REGISTRATIONS = True

#ALLAUTH
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_CONFIRMATION_ANONYMOUS_REDIRECT_URL = LOGIN_URL
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = '/user/all/'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_USERNAME_MIN_LENGTH = 3
ACCOUNT_PASSWORD_MIN_LENGTH =6
ACCOUNT_ADAPTER ="pinry.core.accountadapter.AccountAdapter"
SOCIALACCOUNT_ADAPTER ="pinry.core.accountadapter.SocialAccountAdapter"

#INVITATIONS
INVITE_MODE = True
ACCOUNT_INVITATION_DAYS = 30
ACCOUNT_ACTIVATION_DAYS = 20
INVITATIONS_PER_USER = 5
INVITATION_USE_ALLAUTH = True

#USERS
DEFAULT_USER_GROUP = 'Basic'

#LOCATION
TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
USE_I18N = True
USE_L10N = True
USE_TZ = True

#URLS
ROOT_URLCONF = 'pinry.urls'
INTERNAL_IPS = ['127.0.0.1']

#HTTPS
SECURE_REQUIRED_PATHS = (
    '/admin/',
    '/accounts/',
    '/management/'
)

'''STATIC_PREFIX
The STATIC_URL may not be a full URL on the devserver when files are local.  
The STATIC_PREFIX prepends the STATIC_URL to complete a full URL in templates
css & bookmarklet.
STATIC_PREFIX MUST BE = '' on production.
'''
STATIC_PREFIX = SITE_URL

MEDIA_ROOT = os.path.join(SITE_ROOT, 'media/')
MEDIA_URL = SITE_URL+'/media/'
TMP_ROOT = os.path.join(SITE_ROOT, 'media/tmp/')
TMP_URL = SITE_URL+'/media/tmp/'
STATIC_ROOT = os.path.join(SITE_ROOT, 'static/')
STATIC_URL = '/static/'
#Uplaoded images path
IMAGES_PATH = 'pins/pin/originals/'

# EMAIL
EMAIL_USE_TLS = True
EMAIL_PORT = '587'
EMAIL_HOST = 'smtp.gmail.com'
#TEST EMAIL ON SERVER START
SEND_TEST_EMAIL = False

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
    'pinry.core.middleware.P3PHeaderMiddleware',
    'pinry.core.middleware.SecureRequiredMiddleware',
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
    "pinry.core.context_processors.apiUrl",
    "allauth.account.context_processors.account",
    "allauth.socialaccount.context_processors.socialaccount",
    "invitation.context_processors.remaining_invitations",
) 

COMPRESS_CSS_FILTERS = ['compressor.filters.css_default.CssAbsoluteFilter', 'compressor.filters.cssmin.CSSMinFilter']



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
    'invitation',
)
SOCIALACCOUNT_PROVIDERS ={ 
    'facebook':
        { 'SCOPE': ['email', 'publish_stream'],
          'AUTH_PARAMS': { },
          'METHOD': 'js_sdk'},
    'linkedin':
        { 'SCOPE': ['r_emailaddress', 'r_basicprofile'] }
    }