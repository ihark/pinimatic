from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS

from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization

from pinry.pins.models import Pin
from follow.models import Follow
from django.http import HttpResponse
from django.utils import simplejson as json

#resource path = pinry.api.api.SomeResource

class UserResource(ModelResource):
    #follows = fields.ToManyField('pinry.api.api.FavsResource', 'following', full=True)

    class Meta:
        always_return_data = True
        queryset = User.objects.all()
        resource_name = 'auth/user'
        include_resource_uri = True
        allowed_methods = ['get']
        excludes = ['password']

        #authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
    '''
    def dehydrate(self, bundle):
        #dehydrate follows for only favorites
        for f in bundle.data['follows'][:]:
            if f.data['id'] == None:
                bundle.data['follows'].remove(f)
        return bundle
    '''
    def determine_format(self, request): 
        return "application/json" 

    def apply_authorization_limits(self, request, object_list):
        result = object_list.filter(id=request.user.id)
        return result

class FavsResource(ModelResource):
    user = fields.CharField(attribute='user__username', null=True)
    favid = fields.CharField(attribute='favorite_id', null=True)
    folid = fields.CharField(attribute='folowing_id', null=True)
    
    
    class Meta:
        always_return_data = True
        queryset = Follow.objects.all()
        resource_name = 'favs'
        include_resource_uri = False
        fields = ['favorite']
        allowed_methods = ['get']
        filtering = {
            'favorite': ALL_WITH_RELATIONS,
            'folowing': ALL_WITH_RELATIONS,
            'folid': ALL,
            'favid': ALL,
            'user': ALL_WITH_RELATIONS,
        }
        
        #authentication = BasicAuthentication()
        authorization = DjangoAuthorization()
        
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(FavsResource, self).build_filters(filters)
        
        if 'favid' in filters:
            orm_filters['favorite__id__exact'] = filters['favid']
        if 'folid' in filters:
            orm_filters['folowing__id__exact'] = filters['folid']
        if 'user' in filters:
            orm_filters['user__username__exact'] = filters['user']
        

        return orm_filters
    '''
    def apply_authorization_limits(self, request, object_list):
        return object_list.exclude(favorite__exact=None)
        #.filter(user=request.user)
    '''

        
class PinResource(ModelResource):
    tags = fields.ListField()
    imgUrl = fields.CharField(attribute='imgUrl')
    srcUrl = fields.CharField(attribute='srcUrl')
    repin = fields.ForeignKey('pinry.api.api.PinResource', 'repin', null=True)
    submitter = fields.ForeignKey(UserResource, 'submitter', full = True)
    favorites = fields.ToManyField(FavsResource, 'f_pin', full=True, null=True)
    
    class Meta:
        always_return_data = True
        queryset = Pin.objects.all()
        resource_name = 'pin'
        include_resource_uri = True
        authorization = DjangoAuthorization()
        allowed_methods = ['get', 'post']
        filtering = {
            'published': ['gt'],
            'submitter': ALL_WITH_RELATIONS,
            'fav': ALL_WITH_RELATIONS,
        }

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(PinResource, self).build_filters(filters)

        if 'user' in filters:
            orm_filters['submitter__username__exact'] = filters['user']
        
        if 'favs' in filters:
            orm_filters['f_pin__user__username__exact'] = filters['favs']
        
        if 'tag' in filters:
            orm_filters['tags__name__in'] = filters['tag'].split(',')

        return orm_filters

    def dehydrate_tags(self, bundle):
        return map(str, bundle.obj.tags.all())
    
    def save_m2m(self, bundle):
        tags = bundle.data.get('tags', [])
        bundle.obj.tags.set(*tags)
        return super(PinResource, self).save_m2m(bundle)
    
    def determine_format(self, request): 
        return "application/json" 
        
    '''' no longer needed due to 0.9.11 grade
    def post_list(self, request, **kwargs):
        resp = super(PinResource, self).get_list(request, **kwargs)
        print resp
        return resp
    '''
        
    
    def obj_create(self, bundle, request=None, **kwargs):
        return super(PinResource, self).obj_create(bundle, request, submitter=request.user, uImage=None)   
