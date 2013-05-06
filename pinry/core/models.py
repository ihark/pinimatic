#from pinry.core.admins import *

#handle signals from third party apps
from django.contrib.auth.models import User
from ..pins.models import Pin
from follow import signals

from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives

subject, from_email, to = 'hello', 'from@example.com', 'to@example.com'
text_content = 'This is an important message.'
html_content = '<p>This is an <strong>important</strong> message.</p>'
msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
msg.attach_alternative(html_content, "text/html")
msg.send()

def user_follow_handler(user, target, instance, **kwargs):
    print 'user followed'
    subject = "You have a new follower on %s." %settings.SITE_NAME 
    from_email, to_email = 'from@example.com', [target.email]
    text_content = 'Hey %s,\n\nYou were followed by %s!\n\
                    Go to http://pinimatic.herokuapp.com to check out thier stuff.' % (target, user.username)
    html_content = 'Hey %s,<br><br>You were followed by %s!\n\
                    Check out thier stuff on <a href="http://pinimatic.herokuapp.com/user/%s">%s</a>.' % (target, user, user.id, settings.SITE_NAME)
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def pin_follow_handler(user, target, instance, **kwargs):
    print 'pin followed'
    subject = "Someone digs your stuff on %s." %settings.SITE_NAME 
    from_email, to_email = 'from@example.com', [target.submitter.email]
    text_content = 'Hey %s,\n\n%s just added your pin to thier favorites.  Go to http://pinimatic.herokuapp.com \
                     to check out thier stuff.  Keep up the good work!' % (target.submitter, user)
    html_content = 'Hey %s,<br><br>%s just added your pin to thier favorites.  \n\
                    Check out thier stuff on <a href="http://pinimatic.herokuapp.com/user/%s">%s</a>.\
                    Keep up the good work!' % (target.submitter, user.username, user.id, settings.SITE_NAME)
                    
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()    

signals.followed.connect(user_follow_handler, sender = User, dispatch_uid = 'follow.user')
signals.followed.connect(pin_follow_handler, sender = Pin, dispatch_uid = 'follow.pin')