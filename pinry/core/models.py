#from pinry.core.admins import *

#handle signals from third party apps
from django.contrib.auth.models import User
from ..pins.models import Pin
from django.contrib.comments.models import Comment
from follow.signals import followed
from django.contrib.comments.signals import comment_was_posted, comment_was_flagged

from django.conf import settings
from django.dispatch import receiver
from django.core.mail import send_mail

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context

from django.contrib.sites.models import Site

site = Site.objects.get_current()
site_name = site.name
site_url = 'http://%s/' % site.domain

@receiver(followed, sender=User, dispatch_uid='follow.user')
def user_follow_handler(user, target, instance, **kwargs):
    print kwargs
    if user != target:
        subject = "You have a new follower on %s." %settings.SITE_NAME 
        from_email, to_email = 'from@example.com', [target.email]
        # text_content = 'Hey %s,\n\nYou were followed by %s!\n\
                        # Go to http://pinimatic.herokuapp.com/user/%s/ to check out thier stuff.' % (target, user, user.id)
        # html_content = 'Hey %s,<br><br>You were followed by %s!\n\
                        # Check out thier stuff on <a href="http://pinimatic.herokuapp.com/user/%s/">%s</a>.' % (target, user, user.id, settings.SITE_NAME)
        text_content = get_template('email/email_generic.txt')
        html_content = get_template('email/email_generic.html')
        c = Context({ 'actor': user, 'target': target, 'site_name':site_name, 
                      'site_url': site_url
                   })
        text_content = text_content.render(c)
        html_content = html_content.render(c)
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

@receiver(followed, sender=Pin, dispatch_uid='follow.pin')
def pin_follow_handler(user, target, instance, **kwargs):
    if user != target.submitter:
        subject = "Someone digs your stuff on %s." %settings.SITE_NAME 
        from_email, to_email = 'from@example.com', [target.submitter.email]
        text_content = 'Hey %s,\n\n%s added your pin to thier favorites.  \n\
                        Go to http://pinimatic.herokuapp.com/user/%s/ to check out thier stuff.\
                        Keep up the good work!' % (target.submitter, user, user.id)
        html_content = 'Hey %s,<br><br>%s added your pin to thier favorites.  \n\
                        Check out thier stuff on <a href="http://pinimatic.herokuapp.com/user/%s/">%s</a>.\
                        Keep up the good work!' % (target.submitter, user, user.id, settings.SITE_NAME)
                        
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        
from django.db.models.signals import post_save
#TODO: Also notify pin followers
@receiver(post_save, sender=Comment, dispatch_uid='comment.user')
def pin_comment_handler(sender, *args, **kwargs):
    print 'comment'
    comment = kwargs.pop('instance', None)
    user = comment.user
    target = comment.content_object
    if user != target.submitter:
        subject = "%s commented on your stuff." %user 
        from_email, to_email = 'from@example.com', [target.submitter.email]
        text_content = 'Hey %s,\n\n%s commented on your stuff.  Go to http://pinimatic.herokuapp.com/user/%s/ \
                        to see what they said.' % (target.submitter, user, target.submitter)
        html_content = 'Hey %s,<br><br>%s commented on your stuff.<br>See what they said on \
                        <a href="http://pinimatic.herokuapp.com/user/%s/">%s</a>. \
                        '% (target.submitter, user, target.submitter.id, settings.SITE_NAME)
        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

       