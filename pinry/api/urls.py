from django.conf.urls.defaults import *
from django.conf.urls import patterns, include, url
from tastypie.api import Api
from .api import UserResource, PinResource, FavsResource, ComntResource


v1_api = Api(api_name='v1')
v1_api.register(PinResource())
v1_api.register(UserResource())
v1_api.register(FavsResource())
v1_api.register(ComntResource())

urlpatterns = patterns('',
    (r'', include(v1_api.urls)),
)
