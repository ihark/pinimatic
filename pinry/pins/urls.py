from django.conf.urls import patterns, url


urlpatterns = patterns('pinry.pins.views',
    url(r'^user/all/$', 'recent_pins', name='recent-pins'),
    url(r'^user/\w+/\w+/$', 'recent_pins', name='taged-pins'),
    url(r'^user/\w+/$', 'recent_pins', name='user-pins'),
    url(r'^new-pin/$', 'new_pin', name='new-pin'),
    url(r'^delete-pin/(?P<pin_id>\d+)/$', 'delete_pin', name='delete-pin'),
	url(r'^edit-pin/(?P<pin_id>\d+)/$', 'new_pin', name='edit-pin'),
)
