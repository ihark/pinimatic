from django.contrib.auth.models import User
from tastypie import fields
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS

from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization

from pinry.pins.models import Pin


class UserResource(ModelResource):
    print '---------------UserResource'
    class Meta:
        queryset = User.objects.all()
        resource_name = 'auth/user'
        include_resource_uri = False
        fields = ['username']
        allowed_methods = ['get']
        filtering = {
            'username': ALL,
        }

        # Add it here.
        authorization = DjangoAuthorization()
    

        
class PinResource(ModelResource):  # pylint: disable-msg=R0904
    tags = fields.ListField()
    submitter = fields.ForeignKey( UserResource, 'submitter', full = True)
    print '---------------class PinResource'
    class Meta:
        queryset = Pin.objects.all()
        resource_name = 'pin'
        authorization = DjangoAuthorization()
        filtering = {
            'published': ['gt'],
            'submitter': ALL_WITH_RELATIONS,
        }

    def build_filters(self, filters=None):
        if filters is None:
            filters = {}
        print filters

        orm_filters = super(PinResource, self).build_filters(filters)
        print orm_filters
        if 'user' in filters:
            orm_filters['submitter__username__exact'] = filters['user']
        
        if 'tag' in filters:
            orm_filters['tags__name__in'] = filters['tag'].split(',')
        
        
        
        print orm_filters
        return orm_filters

    def dehydrate_tags(self, bundle):
        return map(str, bundle.obj.tags.all())
    
    def save_m2m(self, bundle):
        print 'SAVE M2M'
        tags = bundle.data.get('tags', [])
        bundle.obj.tags.set(*tags)
        return super(PinResource, self).save_m2m(bundle)



        