from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _
'''notification 1.0
if "notification" in settings.INSTALLED_APPS:
    from notification.models import NoticeType
    def create_notice_types(app, created_models, verbosity, **kwargs):
        if app == NoticeType:
            print 'creating notice types'
            NoticeType.create("followed", _("New Follower"), _("someone started following you"))
            NoticeType.create("favorited", _("New Favorite"), _("someone favorited your pin"))
            NoticeType.create("commented", _("New Comment"), _("someone commented on your pin"))
            NoticeType.create("added", _("New Add"), _("someone added your pin to thier collection"))
            NoticeType.create("system_message", _("System Message"),
                 _("Important information about %s") % settings.SITE_NAME)
    signals.post_syncdb.connect(create_notice_types)
else:
    print "Skipping creation of NoticeTypes as notification app not found"
'''
#notification-1  
if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification
    print '----notice types'
    def create_notice_types(app, created_models, verbosity, **kwargs):
        if app == notification:
            print 'creating notice types'
            notification.create_notice_type("followed", _("New Follower"), _("has followed you"))
            notification.create_notice_type("favorited", _("New Favorite"), _("has favorited your pin"))
            notification.create_notice_type("commented", _("New Comment"), _("has commented on your pin"))
            notification.create_notice_type("added", _("New Add"), _("has added your pin to their collection"))
            notification.create_notice_type("system_message", _("%s Notice") % settings.SITE_NAME,
                 _("important information about %s") % settings.SITE_NAME)
    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"