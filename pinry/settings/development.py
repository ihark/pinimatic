#manage.py uses RACK_ENV to determine the settings file to use
#from pinry.settings.settings import *
from pinry.settings import *
import os

print '--Development Settings Loading'

DEBUG = True
TEMPLATE_DEBUG = DEBUG
HTTPS=1#was used to test https but not used now?

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(SITE_ROOT, 'development.db'),
    }
}


SECRET_KEY = 'fake-key'