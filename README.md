# ![Pinimatic](https://github.com/arctelix/pinimatic/raw/master/logo.png)


Pinimatic is a self-hosted, [Pinterest][0] inspired by [Wookmark][1] and
built on top of Django. Originally started as [Pinry][2], I greatly expanded upon the basic
Pinry it to make a fully functional, socially integrated, pinboard site.  Pinimatic is currently in 
Alpha/Development, some upgrades may be ugly/not work till v1.0.0 is release.

![Pinry Screenshot](https://github.com/arctelix/pinimatic/master/screenshot.png)

## Getting Started

Pinimatic has three different customizable configurations:

### Development

Have virtualenv and pip installed. You may also need to have the build
dependencies for PIL installed.

Note: On Ubuntu you can get the build deps by running
`sudo apt-get build-dep python-imaging`.

    $ git clone git://github.com/overshard/Pinimatic.git
    $ cd Pinimatic
    $ virtualenv .
    $ pip install -r requirements.txt
    $ python manage.py syncdb
    $ python manage.py migrate
    $ python manage.py runserver


### Production

Pinimatic is configured to run on Heroku with Gunicorn in the production environment.
You must configure heroku as follows:
- Create a Heroku account and add postgreSQL to your account.
- Create amazon S3 account and set up a bucket.
- Set Heroku env variable RACK_ENV = production
- Set Heroku env variable SECRET_KEY = any random string
- Set Heroku env variables for the database: DB_USER, DB_PASSWORD, DB_NAME
- Set Heroku env variables for email: EMAIL_HOST_PASSWORD,EMAIL_HOST_USER
  acording to your email smtp server.
- set Heroku env variables AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, S3_BUCKET_NAME
  acording to your amazon S3 bucket.

### Staging
Pinimatic is configured to run on Heroku with the built in devlopment server in the 
staging environment. You must configure heroku the same as above with the following changes:
- Set Heroku env variable RACK_ENV = staging

### Development
Pinimatic is configured to run out of the box with the built in devlopment server in development 
staging environment.
- To enable sending email set local environment variables: EMAIL_HOST_PASSWORD,EMAIL_HOST_USER


### Quick Settings

There are a few settings provided specific to Pinimatic that allow you to get some
of the most requested functionality easily. (Pinimatic/settings/__init__.py)

 + **SITE_NAME**: For quickly changing the name Pinimatic to something you prefer.
 + **ALLOW_NEW_REGISTRATIONS**: Set to False to prevent people from registering.
 + **PUBLIC**: Set to False to require people to register before viewing pins.
   (Note: Setting PUBLIC to False does still allow registrations. Make sure
          both PUBLIC and the previous setting are set to False to prevent
          all public access.)

 + **INVITE_MODE**: Set to true to allow new registraions by invitation only.
   See https://github.com/arctelix/django-invitation.git for more information on invittation settings.
 + **ALLAUTH**: Many settings agailable for customization of login and signup.
   See https://github.com/arctelix/django-allauth.git for more information on allauth settings.
 + **EAMIL**: Configure these settings as per your email smtp server.
   
   
## Current Features
 + Pin Tagging
 + User groups
 + Filter pin views
 + User profiles
 + Add images via Bookmarklet
 + Add images via Upload
 + Add images via URL
 + Delete & Edit Pins
 + Favorite / Follow pins
 + Follow users
 + Re-Pin Pins
 + Comment on pins
 + User profile pages with stats
 + Local User Accounts & Social Connections
 + User Manageable Social Connections
 + User Manageable Email Addresses
 + Registration Invitation Only Mode
 + Invitation Management
 + Admin Email Users Interface
 
## Roadmap
 + User Boards
 + Non-image URL pinning


## License (Simplified BSD)

Copyright (c) Simplex Studio (arctelix)
Copyright (c) Isaac Bythewood

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


[0]: http://pinterest.com/
[1]: http://www.wookmark.com/
[2]: https://github.com/overshard/pinry
