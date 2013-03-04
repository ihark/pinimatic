from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.comments.models import ContentType
from tastypie import fields
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS

from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization

from pinry.pins.models import Pin
from follow.models import Follow
from django.http import HttpResponse
from django.utils import simplejson

from django.db.models import Count, Sum, F
from operator import attrgetter

from django.contrib import messages
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpNoContent, HttpForbidden, HttpGone

from taggit.utils import parse_tags
from pinry.core.utils import format_tags
from pinry.pins.forms import PinForm
from django import forms
from tastypie.validation import CleanedDataFormValidation


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
    
    #0.9.12-alpha restrict users to only thier user object
    def authorized_read_list(self, object_list, bundle):
        result =  object_list.filter(id=bundle.request.user.id)
        return result
    
    ''' depreciated in 0.9.12-alpha
    def apply_authorization_limits(self, request, object_list):
        print '--apply_authorization_limits--'
        print request.user.id
        result = object_list.filter(id=request.user.id)
        return result
    '''
class FavsResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', full=True, null=True)
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

        
class ContentTypeResource(ModelResource):
    #model = fields.CharField(attribute = 'model', null=True)
    
    class Meta:
        queryset = ContentType.objects.all()
        resource_name = "contrib/contenttype"
        fields = ['model']
        allowed_methods = ['get']
        include_resource_uri = False
        def determine_format(self, request): 
            return "application/json" 


class PinResource(ModelResource):

    tags = fields.ListField()
    imgUrl = fields.CharField(attribute='imgUrl')
    srcUrl = fields.CharField(attribute='srcUrl', null=True)
    repinObj = fields.ForeignKey('pinry.api.api.PinResource', 'repinObj', null=True)
    repin = fields.CharField(attribute='repinObj__id', null=True)
    submitter = fields.ForeignKey(UserResource, 'submitter', full = True)
    favorites = fields.ToManyField(FavsResource, 'f_pin', full=True, null=True)
    popularity = fields.DecimalField(attribute='popularity', null=True)
    comments = fields.ToManyField('pinry.api.api.CmntResource', 'comments', full=True, null=True)


    class Meta:
        always_return_data = True
        queryset = Pin.objects.all()
        resource_name = 'pin'
        include_resource_uri = False
        allowed_methods = ['get', 'post', 'delete']
        filtering = {
            'published': ['gt'],
            'submitter': ALL_WITH_RELATIONS,
            'favorites': ALL_WITH_RELATIONS,
            'popularity': ALL,
            'tags': ALL,
        }
        validation = CleanedDataFormValidation(form_class=PinForm)
        #ordering = ['popularity']
        authorization = DjangoAuthorization()
    '''No longer needed since comments foreign relation started working (keeping for reference)
    def obj_get_list(self, bundle, **kwargs):
        print '--obj_get_list--'
        objects = super(PinResource, self).obj_get_list(bundle, **kwargs)
        for p in objects:
            #add comments to pin
            cqs = Comment.objects.filter(object_pk__exact=p.id).order_by('id').values('id', 'user_id', 'comment', 'submit_date', 'is_public')
            p.comments = cqs
            #add user to comments
            for c in cqs:
                uqs = User.objects.filter(id__exact=c['user_id']).values()
                c['user'] = uqs[0]
        return objects
    '''
    
    def apply_filters(self, request, applicable_filters):
        print '---apply_filters----'
        """
        An ORM-specific implementation of ``apply_filters``.

        The default simply applies the ``applicable_filters`` as ``**kwargs``,
        but should make it possible to do more advanced things.

        Here we override to check for a 'distinct' query string variable,
        if it's equal to True we apply distinct() to the queryset after filtering.
        """
        distinct = request.GET.get('distinct', False) == ''
        pop = request.GET.get('pop', False) == ''
        
        if pop:
            qs = self.get_object_list(request).filter(**applicable_filters).annotate(fav_count=Count('f_pin__id', distinct=True), repin_count=Count('repin__id', distinct=True)).distinct()
            return qs
        if distinct:
            return self.get_object_list(request).filter(**applicable_filters).annotate(fav_count=Count('f_pin__id', distinct=True), repin_count=Count('repin__id', distinct=True)).distinct()
        else:
            return self.get_object_list(request).filter(**applicable_filters).annotate(fav_count=Count('f_pin__id', distinct=True), repin_count=Count('repin__id', distinct=True))
    
    
    def apply_sorting(self, objects, options=None):
        print '---apply_sorting----'
        if options and "sort" in options:
            if options['sort'] == "popularity":
                #this is wrong, need to get how many times a pin is repinned. This is counting the fact that it was repinned from another pin.
                for p in objects:
                    p.popularity = p.fav_count+(p.repin_count*1.25)

            return sorted(objects, key=attrgetter(options['sort']), reverse=True)
 
        return super(PinResource, self).apply_sorting(objects, options)

    def build_filters(self, filters=None):
        print '---build filters---'
        if filters is None:
            filters = {}

        orm_filters = super(PinResource, self).build_filters(filters)
        #test for fields# orm_filters['tagged_items'] = 'true'
            
        if 'user' in filters:
            orm_filters['submitter__username__exact'] = filters['user']
            
        
        if 'favs' in filters:
            if filters['favs'] == 'all':
                orm_filters['f_pin__folowing__isnull'] = 'true'
            else:
                orm_filters['f_pin__user__username__exact'] = filters['favs']

        if 'pop' in filters:
                #print self.obj_get(None, pk=1)
                orm_filters['f_pin__folowing__isnull'] = 'true'
                #orm_filters['order_by__fav_count']
                

        if 'tag' in filters:
            orm_filters['tags__name__in'] = filters['tag'].split(',')
        

        return orm_filters
    
    def dehydrate_tags(self, bundle):
        return map(str, bundle.obj.tags.all())
        
    def hydrate_tags(self, bundle):
        #if one tagsUser is recieved convert string to a list
        try: 
            tagsUser = bundle.data['tagsUser']
            if type(tagsUser) == str:
                bundle.data['tagsUser'] = [tagsUser]
        except: pass
        #hydrate tags is handled by form validation!
        return bundle
        
    def save_m2m(self, bundle):
        tags = bundle.data.get('tags', [])
        bundle.obj.tags.set(*tags)
        return super(PinResource, self).save_m2m(bundle)
    
    def determine_format(self, request): 
        return "application/json" 
        
    ''' no longer needed due to 0.9.11 grade
    def post_list(self, request, **kwargs):
        resp = super(PinResource, self).get_list(request, **kwargs)
        print resp
        return resp
    '''
    def obj_create(self, bundle, **kwargs):
        print '----obj_create------'
        repinUrl = '/api/v1/pin/'+bundle.data['repin']+'/'
        bundle = super(PinResource, self).obj_create(bundle, repinObj=repinUrl,  submitter=bundle.request.user, uImage=None, comments=[])
        return bundle
        

    def obj_delete(self, bundle, **kwargs):
            if not hasattr(bundle.obj, 'delete'):
                try:
                    bundle.obj = self.obj_get(bundle=bundle, **kwargs)
                except ObjectDoesNotExist:
                    raise NotFound("A model instance matching the provided arguments could not be found.")
            if bundle.request.user == bundle.obj.submitter:
                self.authorized_delete_detail(self.get_object_list(bundle.request), bundle)
                bundle.obj.delete()
                bundle.data = {"django_messages": [{"extra_tags": "alert alert-success", "message": 'Delete was successfull.', "level": 25}]}
                print bundle
                #using HttpGone in stead of HttpNoContent so success can be displaied.
                #TODO: how to add message to normal tasypie responce instead of forcing it here.  
                #Also, why is it not getting picked up by middleware, so i can gust use django messages.
                raise ImmediateHttpResponse(self.create_response(bundle.request, bundle, response_class = HttpGone))
            else:
                bundle.data = {"django_messages": [{"extra_tags": "alert alert-error", "message": 'You can not delete other users pins.', "level": 25}]}
                print bundle
                raise ImmediateHttpResponse(self.create_response(bundle.request, bundle, response_class = HttpForbidden))
        
        
class CmntResource(ModelResource):
    user = fields.ToOneField('pinry.api.api.UserResource', 'user', full=True)
    content_type_id = fields.CharField(attribute = 'content_type_id')
    site_id = fields.CharField(attribute = 'site_id')
    content_object = GenericForeignKeyField({
        Pin: PinResource,
    }, 'content_object', null=True)
    
    class Meta:
        always_return_data = True
        queryset = Comment.objects.all()
        resource_name = 'cmnt'
        include_resource_uri = False
        allowed_methods = ['get', 'post', 'delete']
        filtering = {
            'object_pk': ALL_WITH_RELATIONS,
            'content_type': ALL_WITH_RELATIONS,
        }
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

    def obj_create(self, bundle, **kwargs):
        print '----obj_create------'
        bundle = super(CmntResource, self).obj_create(bundle, user=bundle.request.user)
        return bundle