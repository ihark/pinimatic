from django.conf.urls import patterns, url


urlpatterns = patterns('',
    url(r'^$', 'pinry.core.views.home', name='home'),
    url(r'^private/$', 'pinry.core.views.private', name='private'),
    url(r'^loggedout/$', 'pinry.core.views.logged_out', name='logged_out'),
    url(r'^help/$', 'pinry.core.views.help', name='help'),
    url(r'^bookmarklet/$', 'pinry.core.views.bookmarklet', name='bookmarklet'),
    url(r'^ajax/thumb/$', 'pinry.core.utils.ajax_upload', name='ajax_upload'),
    url(r'^ajax/submit/$', 'pinry.pins.views.AjaxSubmit', name='AjaxSubmit'),
    url(r'^ajax/thumb/(?P<fileName>.+)$', 'pinry.core.utils.delete_upload', name='delete_upload'),
    url(r'^contact/$', 'pinry.core.views.contact', name='contact'),
    url(r'^accounts/relationships/$', 'pinry.core.views.relationships', name='relationships'),
    url(r'^unfollow/(?P<app>[^\/]+)/(?P<model>[^\/]+)/(?P<id>\d+)/(?P<user_id>\d+)/$', 'pinry.core.views.unfollow', name='unfollow'),
    url(r'^unfollow/(?P<follow_id>\d+)/$', 'pinry.core.views.unfollow_by_id', name='unfollow'),
)
