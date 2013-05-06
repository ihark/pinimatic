from django.conf import settings
from django.db.models import signals
from django.utils.translation import ugettext_noop as _

if "notification" in settings.INSTALLED_APPS:
    from notification.models import NoticeType

    def create_notice_types(app, created_models, verbosity, **kwargs):
        NoticeType.create("followed", _("New Follower"), _("someone started following you"))
        NoticeType.create("favorited", _("New Favorite"), _("someone favorited your pin"))
        NoticeType.create("commented", _("New Comment"), _("someone commented on your pin"))
        NoticeType.create("added", _("New Add"), _("someone added your pin to thier collection"))
        NoticeType.create("system_message", _("System Message"),
             _("Important information about %s") % settings.SITE_NAME)
    signals.post_syncdb.connect(create_notice_types, sender=NoticeType)
else:
    print "Skipping creation of NoticeTypes as notification app not found"