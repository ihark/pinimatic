#from pinry.settings.settings import *
from pinry.settings import *

import os


DEBUG = True
TEMPLATE_DEBUG = DEBUG
HTTPS=1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(SITE_ROOT, 'development.db'),
    }
}


SECRET_KEY = 'fake-key'
