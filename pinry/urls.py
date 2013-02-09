from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/', include('pinry.api.urls')),
    url(r'', include('pinry.core.urls', namespace='core')),
    url(r'', include('pinry.pins.urls', namespace='pins')),
    url('^', include('follow.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/tmp/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.TMP_ROOT,
        }),
   )