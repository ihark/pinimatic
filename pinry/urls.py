from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.views.generic import TemplateView

admin.autodiscover()
handler500 = 'pinry.core.views.custom_500'

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('pinry.api.urls')),
    url(r'', include('pinry.core.urls', namespace='core')),
    url(r'', include('pinry.pins.urls', namespace='pins')),
    url('^', include('follow.urls')),
    #TODO: is the temp dir better on amazon or heroku?
    url(r'^media/tmp/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.TMP_ROOT,
    }),
    url(r'^comments/', include('django.contrib.comments.urls')),
    (r'^accounts/', include('invitation.urls')),
    (r'^accounts/', include('allauth.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


#provide url for testing error pages
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^500/$', 'pinry.core.views.custom_500'),
        (r'^404/$', 'django.views.generic.simple.direct_to_template', {'template': '404.html'}),
    )

#url patters for local static and media files
if settings.SITE_IP.split('.')[0] == '192':
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
    )
if settings.SITE_IP.split('.')[0] == '192':#and settings.DEBUG == False
    urlpatterns += patterns('',
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.STATIC_ROOT,
        }),
    )    