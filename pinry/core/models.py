#from pinry.core.admins import *

#handle signals from third party apps
from django.contrib.auth.models import User
from ..pins.models import Pin
from django.contrib.comments.models import Comment
from django.db.models.signals import post_save
from follow.signals import followed
from django.contrib.comments.signals import comment_was_posted, comment_was_flagged

from django.contrib.sites.models import Site
from django.conf import settings
from django.dispatch import receiver
from django.core.mail import send_mail

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context



site = Site.objects.get_current()
site_name = site.name
site_url = 'http://%s/' % site.domain

#REFERENCE: notification.send(users, label, extra_context=None, sender=None)
#TODO: when notification is imported before  functions with DEBUG=Flase on heroku we get an import error
#but works with DEBUG=T/F on dev server?

@receiver(followed, sender=User, dispatch_uid='follow.user')
def user_follow_handler(user, target, instance, **kwargs):
    from notification import models as notification
    '''
    user: the user who acted
    target: the user that has been followed
    instance: the follow object
    '''
    if user != target:
        notification.send([target], "followed", {"from_user": user}, sender=user)
        '''KEEP THIS HERE AS REFERENCE FOR USING THE EMIAL SYSTEM
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
        '''
@receiver(followed, sender=Pin, dispatch_uid='follow.pin')
def pin_follow_handler(user, target, instance, **kwargs):
    '''
    user: the user who acted
    target: the pin that has been followed
    instance: the follow object
    '''
    from notification import models as notification
    if user != target.submitter:
        notification.send([target.submitter], "favorited", {"from_user": user}, sender=target)
        
#TODO: Also notify pin followers, use observe notification
@receiver(post_save, sender=Comment, dispatch_uid='comment.user')
def pin_comment_handler(sender, *args, **kwargs):
    comment = kwargs.pop('instance', None)
    print comment
    user = comment.user
    target = comment.content_object
    from notification import models as notification
    notification.send_observation_notices_for(target, "commented", {"from_user": user}, [user])
    if user != target.submitter:
        notification.send([target.submitter], "commented", {"from_user": user}, sender=target)
        notification.observe(target, user, "commented")

       