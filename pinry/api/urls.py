from django.conf.urls.defaults import *
from django.conf.urls import patterns, include, url
from tastypie.api import Api
from .api import UserResource, PinResource


v1_api = Api(api_name='v1')
v1_api.register(PinResource())
v1_api.register(UserResource())

urlpatterns = patterns('',
    (r'', include(v1_api.urls)),
)
