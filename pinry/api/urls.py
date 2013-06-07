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
from .api import RepinsResource
from .api import AvatarResource

v1_api = Api(api_name='v1')
v1_api.register(PinResource())
v1_api.register(UserResource())
v1_api.register(FavsResource())
v1_api.register(CmntResource())
v1_api.register(ContentTypeResource())
v1_api.register(FollowsResource())
v1_api.register(PinTagResource())
v1_api.register(RepinsResource())
v1_api.register(AvatarResource())

urlpatterns = patterns('',
    (r'', include(v1_api.urls)),
)
