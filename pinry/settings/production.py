from pinry.settings import *

import os


DEBUG = True
TEMPLATE_DEBUG = DEBUG

# TODO: I recommend using psycopg2 w/ postgres but sqlite3 is good enough.
# DATABASES = {
    # 'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(SITE_ROOT, 'production.db'),
    # }
# }
# heroku Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
    }
}
# TODO: Be sure to set this.
SECRET_KEY = 'Ydj2keidk569eo3k4786i6k84f3khye'

