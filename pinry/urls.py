from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()
handler500 = 'pinry.core.views.custom_500'

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('pinry.api.urls')),
    url(r'', include('pinry.core.urls', namespace='core')),
    url(r'', include('pinry.pins.urls', namespace='pins')),
    url('^', include('follow.urls', namespace='follow')),
    #TODO: is the temp dir better on amazon or heroku?
    url(r'^media/tmp/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.TMP_ROOT,
    }),
    url(r'^comments/', include('django.contrib.comments.urls')),
    (r'^accounts/', include('invitation.urls')),
    (r'^accounts/', include('allauth.urls')),
    (r'^accounts/notifications/', include('notification.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# test this
urlpatterns += staticfiles_urlpatterns()

#provide url for testing error pages
if not settings.RACK_ENV:
    urlpatterns += patterns('',
        (r'^500/$', 'pinry.core.views.custom_500'),
        (r'^404/$', 'django.views.generic.simple.direct_to_template', {'template': '404.html'}),
        (r'^email/$', 'django.views.generic.simple.direct_to_template', {'template': 'notification/default/email_body.html'}),
    )

#url patters for local static and media files
if not settings.RACK_ENV:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
#enables dev server to serve static files with compressor & collect static
if not settings.RACK_ENV:
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT, 'show_indexes': True
        }),
    )    