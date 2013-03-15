from django.conf import settings

print '--core/admins.py'

#ADMINS setup: These users will get 500 error emails
from django.contrib.auth.models import User
admins = User.objects.filter(is_superuser__exact=True)
settings.ADMINS = []
for u in admins:
    settings.ADMINS.append((u.username, u.email))
print 'ADMINS: ', settings.ADMINS

#SEND TEST EMAIL
if settings.SEND_TEST_EMAIL:
    from django.core.mail import send_mail, mail_admins
    #send_mail('DEVELOPMENT SERVER STARTED', 'The server has been started @ '+settings.SITE_URL, 'pinimatic@gmail.com', ['jpogrob@gmail.com'], fail_silently=False)
    mail_admins('AMDINS: SEVER HAS BEEN STARTED', 'The server has been started @ '+settings.SITE_URL, fail_silently=False)
    print 'Test email sent to ADMINS, set SEND_TEST_EMAIL=False to stop this'