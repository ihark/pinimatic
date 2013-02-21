from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'pinry.core.views.home', name='home'),
    url(r'^private/$', 'pinry.core.views.private', name='private'),
    url(r'^login/$', 'django.contrib.auth.views.login',
        {'template_name': 'core/login.html'}, name='login'),
    url(r'^register/$', 'pinry.core.views.register', name='register'),
    url(r'^logout/$', 'pinry.core.views.logout_user', name='logout'),
    url(r'^help/$', 'pinry.core.views.help', name='help'),
    url(r'^bookmarklet/$', 'pinry.core.views.bookmarklet', name='bookmarklet'),
    url(r'^ajax/thumb/$', 'pinry.core.utils.ajax_upload', name='ajax_upload'),
    url(r'^ajax/submit/$', 'pinry.pins.views.AjaxSubmit', name='AjaxSubmit'),
    url(r'^ajax/thumb/(?P<fileName>.+)$', 'pinry.core.utils.delete_upload', name='delete_upload'),
)
