from django.conf.urls.defaults import *
from django.conf.urls import patterns, include, url
from tastypie.api import Api
from .api import UserResource
from .api import PinResource
from .api import FavsResource
from .api import CmntResource
from .api import ContentTypeResource
from .api import FollowsResource
from .api import PinTagResource

v1_api = Api(api_name='v1')
v1_api.register(PinResource())
v1_api.register(UserResource())
v1_api.register(FavsResource())
v1_api.register(CmntResource())
v1_api.register(ContentTypeResource())
v1_api.register(FollowsResource())
v1_api.register(PinTagResource())

urlpatterns = patterns('',
    (r'', include(v1_api.urls)),
)
