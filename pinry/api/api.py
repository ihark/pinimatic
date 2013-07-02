from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.comments.forms import CommentForm
from django.contrib.comments.models import ContentType
from tastypie import fields
from tastypie.contrib.contenttypes.fields import GenericForeignKeyField
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS

from tastypie.authentication import BasicAuthentication
from tastypie.authorization import DjangoAuthorization

from pinry.pins.models import Pin
from follow.models import Follow
from avatar.models import Avatar
from avatar.util import get_default_avatar_url

from django.http import HttpResponse
from django.utils import simplejson

from django.db.models import Count, Sum, F
from operator import attrgetter, itemgetter

from django.contrib import messages
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.http import HttpNoContent, HttpForbidden, HttpGone, HttpCreated

from taggit.utils import parse_tags
from pinry.core.utils import format_tags
from pinry.pins.forms import PinForm
from django import forms
from tastypie.validation import CleanedDataFormValidation

from django.core.files.storage import default_storage
from tastypie.serializers import Serializer
from django.core.urlresolvers import reverse
from tastypie.exceptions import Unauthorized
from pinry.core.templatetags.email import smartdate

from django.db.models import Q
import operator
from collections import Counter



#resource path = pinry.api.api.SomeResource

class DjangoAuthorizationLimits(DjangoAuthorization):

    def create_list(self, object_list, bundle):
        # Assuming their auto-assigned to ``user``.
        return object_list

    def create_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        user = getattr(bundle.obj, 'user', None)
        if not user: user = getattr(bundle.obj, 'submitter', None)
        if user and user != bundle.request.user:
            raise Unauthorized("Sorry, not your's.")
        else:
            return True

    def update_list(self, object_list, bundle):
        allowed = []
        # Since they may not all be saved, iterate over them.
        for obj in object_list:
            # Is the requested object owned by the user?
            user = getattr(obj, 'user', None)
            if not user: user = getattr(obj, 'submitter', None)
            if user and user == bundle.request.user:
                allowed.append(obj)

        return allowed

    def update_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        user = getattr(bundle.obj, 'user', None)
        if not user: user = getattr(bundle.obj, 'submitter', None)
        print user, bundle.request.user
        if user and user != bundle.request.user:
            raise Unauthorized("Sorry, not your's.")
        else:
            return True

    def delete_list(self, object_list, bundle):
        # Sorry user, no list deletes!
        raise Unauthorized("Sorry, no list deletes.")
    
    def delete_detail(self, object_list, bundle):
        # Is the requested object owned by the user?
        user = getattr(bundle.obj, 'user', None)
        if not user: user = getattr(bundle.obj, 'submitter', None)
        if user and user != bundle.request.user:
            raise Unauthorized("Sorry, not your's.")
        else:
            return True
        
class UserResource(ModelResource):
    #follows = fields.ToManyField('pinry.api.api.FavsResource', 'following', full=True)
    avatar = fields.ToManyField('pinry.api.api.AvatarResource', attribute=lambda bundle: Avatar.objects.filter(user=bundle.obj, primary=True), null=True, full=True)
    class Meta:
        always_return_data = True
        queryset = User.objects.all()
        resource_name = 'auth/user'
        include_resource_uri = True
        allowed_methods = ['get']
        excludes = ['password']
        serializer = Serializer(formats=['json', 'jsonp', 'xml', 'yaml', 'html', 'plist'])

        #authentication = BasicAuthentication()
        authorization = DjangoAuthorizationLimits()

    def determine_format(self, request): 
        return "application/json" 
    
    #0.9.12-alpha restrict users to only thier user object
    def authorized_read_list(self, object_list, bundle):
        result =  object_list.filter(id=bundle.request.user.id)
        return result
    
    #handle anonomus users
    def alter_list_data_to_serialize(self, request, bundle):
        try:
            bundle['objects'][0]
        except:
            bundle['objects']=[{'id':'', 'username':'anonymous'}]
        return bundle
        
    def dehydrate(self, bundle):
        #make sure all users have an avatar and avatar = url
        avatar = bundle.data['avatar']
        if not avatar:
            size = bundle.request.GET.get('avs', 40)
            bundle.data['avatar'] = get_default_avatar_url(bundle.obj, size)
        else:
            bundle.data['avatar'] = avatar[0].data['url']
        return bundle
        
class AvatarResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', null=True)
    
    class Meta:
        always_return_data = True
        queryset = Avatar.objects.all()
        resource_name = 'avatars'
        include_resource_uri = True
        allowed_methods = ['get']
        fields = ['id','primary']
        filtering = {
            'primary': ALL,
            'user': ALL_WITH_RELATIONS,
            'size': ALL,
        }
        serializer = Serializer(formats=['json', 'jsonp', 'xml', 'yaml', 'html', 'plist'])

        #authentication = BasicAuthentication()
        authorization = DjangoAuthorizationLimits()

    def determine_format(self, request): 
        return "application/json" 
    
    def alter_list_data_to_serialize(self, request, bundle):
        #for obj in bundle['objects']:
            #del obj.data['user']
        return bundle
       
    def alter_detail_data_to_serialize(self, request, bundle):
        #del bundle.data['user']
        return bundle
    
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(AvatarResource, self).build_filters(filters)
        
        if 'p' in filters:
            orm_filters['primary__exact'] = 'true'
        
        if 'user' in filters:
            orm_filters['user__id__exact'] = filters['user']

        return orm_filters
    
    def dehydrate(self, bundle):
        size = bundle.request.GET.get('avs', 40)
        avatar = bundle.obj
        bundle.data['url'] = avatar.avatar_url(int(size))
        #bundle.data['user'] = {'username':avatar.user.username.title(), 'id':avatar.user.id, 'url':reverse('pins:profile',kwargs={'profileId': avatar.user.id})}
        return bundle
    
#not currently used due to solution in pin resource    
class RepinsResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', null=True, full=True)
    repin_from = fields.CharField(attribute='repin__id')


    class Meta:
        always_return_data = True
        queryset = Pin.objects.filter(repin__isnull=False)
        resource_name = 'repins'
        include_resource_uri = False
        allowed_methods = ['get']
        fields=['pk', 'id']
        filtering = {
            'id': ALL_WITH_RELATIONS,
            'user': ALL_WITH_RELATIONS,
        }
        
        #authentication = BasicAuthentication()
        authorization = DjangoAuthorizationLimits()
        
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(RepinsResource, self).build_filters(filters)
        '''
        if 'favid' in filters:
            orm_filters['favorite__id__exact'] = filters['favid']
        '''

        return orm_filters
    
    def determine_format(self, request): 
        return "application/json"     
    '''
    def apply_authorization_limits(self, request, object_list):
        return object_list.exclude(favorite__exact=None)
        #.filter(user=request.user)
    '''
class FavsResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', null=True, full=True)
    favid = fields.CharField(attribute='favorite_id', null=True)
    #folid = fields.CharField(attribute='folowing_id', null=True)
    
    
    class Meta:
        always_return_data = True
        queryset = Follow.objects.filter(folowing__isnull=True)
        resource_name = 'favs'
        include_resource_uri = False
        fields = ['favorite', 'user']
        allowed_methods = ['get']
        filtering = {
            'favorite': ALL_WITH_RELATIONS,
            'folowing': ALL_WITH_RELATIONS,
            'folid': ALL,
            'favid': ALL,
            'user': ALL_WITH_RELATIONS,
        }
        
        #authentication = BasicAuthentication()
        authorization = DjangoAuthorizationLimits()
        
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(FavsResource, self).build_filters(filters)
        
        if 'favid' in filters:
            orm_filters['favorite__id__exact'] = filters['favid']
        if 'folid' in filters:
            orm_filters['folowing__id__exact'] = filters['folid']
        if 'user' in filters:
            orm_filters['user__id__exact'] = filters['user']

        return orm_filters
    
    def determine_format(self, request): 
        return "application/json"     
    '''
    def apply_authorization_limits(self, request, object_list):
        return object_list.exclude(favorite__exact=None)
        #.filter(user=request.user)
    '''

class FollowsResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', null=True)
    folowing = fields.ForeignKey(UserResource, 'folowing', null=True)

    class Meta:
        always_return_data = True
        queryset = Follow.objects.filter(favorite__isnull=True)
        resource_name = 'follows'
        include_resource_uri = False
        excludes = ['id']
        allowed_methods = ['get']
        filtering = {
            'folowing': ALL_WITH_RELATIONS,
            'user': ALL_WITH_RELATIONS,
        }
        
        #authentication = BasicAuthentication()
        authorization = DjangoAuthorizationLimits()
        
    def build_filters(self, filters=None):
        if filters is None:
            filters = {}

        orm_filters = super(FollowsResource, self).build_filters(filters)
        
        if 'fing' in filters:
            orm_filters['user__id__exact'] = filters['fing']
        if 'fers' in filters:
            orm_filters['folowing__id__exact'] = filters['fers']

        return orm_filters
    
    def determine_format(self, request): 
        return "application/json" 
    
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
        allowed_methods = ['get']
        include_resource_uri = False
        
    def determine_format(self, request): 
        return "application/json" 

import itertools
import collections

class PinResource(ModelResource):

    tags = fields.ListField()
    imgUrl = fields.CharField(attribute='imgUrl')
    srcUrl = fields.CharField(attribute='srcUrl', null=True)
    repinedObj = fields.ForeignKey('pinry.api.api.PinResource', 'repin', null=True)
    repined = fields.CharField(attribute='repin__id', null=True)
    repins = fields.ToManyField('pinry.api.api.PinResource', attribute=lambda bundle: Pin.objects.filter(repin=bundle.obj.id), null=True, full=True)
    submitter = fields.ForeignKey(UserResource, 'submitter', full = True)
    favorites = fields.ToManyField(FavsResource, 'f_pin', full=True, null=True)
    popularity = fields.DecimalField(attribute='popularity', null=True)
    comments = fields.ToManyField('pinry.api.api.CmntResource', 'comments', full=True, null=True)

    current_search = None
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
        #authorization = DjangoAuthorization()
        authorization = DjangoAuthorizationLimits()

    
    def apply_filters(self, request, applicable_filters):
        #P '---apply_filters----'
        """
        An ORM-specific implementation of ``apply_filters``.

        The default simply applies the ``applicable_filters`` as ``**kwargs``,
        but should make it possible to do more advanced things.

        Here we override to check for a 'distinct' query string variable,
        if it's equal to True we apply distinct() to the queryset after filtering.
        """
        distinct = request.GET.get('distinct', False) == ''#for general use
        pop = request.GET.get('pop', False) == ''#for popular view
        tagsFilter = request.GET.get('tagsF', False)#for normal tag filtering
        
        #Base query set (must be disctnct so that i can be combined with other distict qs)
        qs = self.get_object_list(request).filter(**applicable_filters).distinct()
        
        if tagsFilter:
            tagsFilter = tagsFilter.rstrip(',').split(',')
            for t in tagsFilter:
                qs = qs.filter(tags__name__exact=t)
        
        if pop:
            qs = qs.annotate(fav_count=Count('f_pin__id', distinct=True)).distinct()
        
        if distinct:
            qs =  qs.distinct()
        
        #text search
        text_search = request.GET.get('textSearch', False)
        merged_qs = []
        if text_search:
            #field options
            desc_search = request.GET.get('in', False) == 'desc'
            tag_search = request.GET.get('in', False) == 'tag'
            cmnt_search = request.GET.get('in', False) == 'cmnt'
            user_search = request.GET.get('in', False) == 'user'
            #operator options
            search_and = request.GET.get('and', False) == ''
            tag_opr = request.GET.get('tagAnd', 'or_')
            desc_opr = request.GET.get('descAnd', 'or_')
            cmnt_opr = request.GET.get('cmntAnd', 'or_')
            #operator validation
            if tag_opr not in ['or_','and_']: tag_opr = 'or_'
            if desc_opr not in ['or_','and_']: desc_opr = 'or_'
            if cmnt_opr not in ['or_','and_']: cmnt_opr = 'or_'
            
            #apply search string to slected search fields
            if not (tag_search or desc_search or cmnt_search):
                tag_search = text_search
                desc_search = text_search
                cmnt_search = text_search
            else:
                if tag_search: tag_search = text_search
                if desc_search: desc_search = text_search
                if cmnt_search: cmnt_search = text_search
            
            #user search is special, must be expicity chosen
            if user_search: user_search = text_search
                
            #tests
            #text_search = 'light cool'
            print 'text_search', text_search
            print 'tag_search', tag_search
            print 'desc_search', desc_search
            print 'cmnt_search', cmnt_search
            print 'user_search', user_search

            print 'tag_opr', tag_opr
            print 'desc_opr', desc_opr
            print 'cmnt_opr', cmnt_opr
            print 'search_and', search_and
            
            self.current_search=text_search
            
            is_search = text_search
            search_qsl = []
            text_search = filter(None, text_search.split(' '))
            if tag_search:# TEXT SEARCH: for partial words sorted by number of occurances in each field
                tag_qs = qs.filter(reduce(getattr(operator,tag_opr), (Q(tags__name__icontains=x) for x in text_search))).distinct()
                #tag_qs = tag_qs.annotate(tag_rank=Count('tags__name', distinct=True))
                #tag_qs = tag_qs.order_by('tag_rank').reverse()
                print 'tag_qs', tag_qs.count()
                search_qsl.append(tag_qs)
            if desc_search:
                desc_qs = qs.filter(reduce(getattr(operator,desc_opr), (Q(description__icontains=x) for x in text_search))).distinct()
                search_qsl.append(desc_qs)
            if cmnt_search:
                cmntqs = Comment.objects.filter(content_type__name = 'pin', site_id=settings.SITE_ID )
                cmntqs = cmntqs.filter(reduce(getattr(operator,cmnt_opr), (Q(comment__icontains=x) for x in text_search))).distinct()
                cmnts = list(cmntqs.values('object_pk'))
                if len(cmnts)>0:
                    cmnt_qs = qs.filter(reduce(operator.or_, (Q(pk__exact=int(x['object_pk'])) for x in cmnts))).distinct()
                    #create dictionary of object_pk:rank
                    cmnts = {str(i['object_pk']):0 for i in cmnts}
                    search_qsl.append(cmnt_qs)
                    #populate cmnts with rank
                    for ci in cmntqs:
                        rank = 0
                        print '--cmnt=', ci.comment
                        for w in text_search:
                            rank +=  ci.comment.lower().count(w.lower())
                            print 'w rank:', rank, w.lower()
                        cmnts[str(ci.object_pk)] += rank
                        print 'TC rank:', rank, cmnts
                else: 
                    cmnt_qs = []
                    cmnts = {}
            
            #merge all query sets
            for sqs in search_qsl:
                if len(merged_qs)>0 and search_and:
                    print 'and merge'
                    merged_qs &= sqs
                elif len(merged_qs)>0:
                    merged_qs |= sqs
                else:
                    merged_qs = sqs
            
            #filter for user
            if user_search:
                merged_qs = merged_qs.filter(reduce(operator.or_, (Q(submitter__username__icontains=x) for x in text_search))).distinct()
            
            #add ranks to merged_qs
            for i in merged_qs:
                rank = 0
                print 'i--------------', i.id
                if tag_search and i in tag_qs:
                    rank = 0
                    for w in text_search:
                        for t in i.tags.all():
                            #print 't', t, t.name.lower().count(w.lower())
                            rank +=  t.name.lower().count(w.lower())
                    i.tag_rank = rank
                rank = 0
                if desc_search and i in desc_qs:
                    rank = 0
                    for w in text_search:
                        rank +=  i.description.lower().count(w.lower())
                    i.desc_rank = rank
                if cmnt_search and i in cmnt_qs:
                    i.cmnt_rank = cmnts[str(i.id)]

            if not merged_qs and is_search:
                messages.error(request, 'No reuts for your search.')

        return merged_qs or qs
        

    
    def apply_sorting(self, objects, options=None):
        #API---apply_sorting----'
        
        if options and "sort" in options:
            if options['sort'] == "popularity":
                for p in objects:
                    cmnts = p.comments.count()
                    repins = Pin.objects.filter(repin=p.id).count()
                    p.popularity = p.fav_count+(repins*1.25)+(cmnts*.25)
            ordered_pop = sorted(objects, key=attrgetter(options['sort']), reverse=True)
            return ordered_pop
        
        for o in objects:
            print '----------------------------------'
            print 'getting rang for pin#: ', o.id
            o.search_rank = 0
            if getattr(o, 'tag_rank', False):
                print 'is_tag_search:', o.tag_rank
                #tags are already sorted
                #return objects
                o.search_rank += o.tag_rank * 1
                
            if getattr(o, 'user_rank', False):
                print 'is_user_search:', o.user_rank
                #return objects
                o.search_rank += o.user_rank * 1
                
            if getattr(o, 'desc_rank', False):
                print 'is_desc_search:', o.desc_rank
                #ordered_desc = sorted(objects, key=attrgetter('desc_rank'), reverse=True)
                #return ordered_desc
                o.search_rank += o.desc_rank * .5
            
            if getattr(o, 'cmnt_rank', False):
                print 'is_cmnt_search:', o.cmnt_rank
                #ordered_cmnt = sorted(objects, key=attrgetter('cmnt_rank'), reverse=True)
                #return ordered_cmnt
                o.search_rank += o.cmnt_rank * .25

            print '=====total o.search_rank = ',o.search_rank

            
        ordered_objects = sorted(objects, key=attrgetter('search_rank'), reverse=True)
        return ordered_objects

        return super(PinResource, self).apply_sorting(objects, options)

    def build_filters(self, filters=None):
        #P'---build filters---'
        if filters is None:
            filters = {}

        orm_filters = super(PinResource, self).build_filters(filters)
            
        if 'user' in filters:
            orm_filters['submitter__id__exact'] = filters['user']
            
        if 'favs' in filters:
            if filters['favs'] == 'all':
                orm_filters['f_pin__folowing__isnull'] = 'true'
            else:
                orm_filters['f_pin__user__id__exact'] = filters['favs']
                
        if 'fers' in filters:
            followers = Follow.objects.filter(favorite__isnull=True).filter(folowing__id__exact = filters['fers']).values_list('user__id', flat=True)
            orm_filters['submitter__id__in'] = followers
            
        if 'fing' in filters:
            following = Follow.objects.filter(favorite__isnull=True).filter(user__id__exact = filters['fing']).values_list('folowing__id', flat=True)
            orm_filters['submitter__id__in'] = following

        if 'pop' in filters:
                orm_filters['f_pin__folowing__isnull'] = 'true'
        '''
        if 'tag' in filters:
            orm_filters['tags__name__in'] = filters['tag'].rstrip(',')
        '''
        if 'cmnts' in filters:
            comments = Comment.objects.filter(user__id=filters['cmnts'], content_type__name = 'pin', site_id=settings.SITE_ID ).values_list('object_pk', flat=True)
            comments = [int(c) for c in comments].values_list('object_pk', flat=True)
            orm_filters['pk__in'] = comments

        return orm_filters
    
    def alter_list_data_to_serialize(self, request, bundle):
        #TODO: make an object for search data and filter
        bundle['search'] = self.current_search
        bundle['filter'] = 'not implimented'
        mstore = messages.get_messages(request)
        for m in mstore: 
            bundle['django_messages'] = [{"extra_tags": m.tags, "message": m, "level": m.level}]
            
        
        for obj in bundle['objects']:
            #obj.data['meta']
            pass

            
            
        return bundle
    
    def dehydrate_tags(self, bundle):
        return map(str, bundle.obj.tags.all())
    
    
    def dehydrate_published(self, bundle):
        return {'l':bundle.obj.smartdate(), 's':bundle.obj.smartdate('short'), 'd':bundle.obj.smartdate('dot')}
        
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
        #P resp
        return resp
    '''
    def obj_create(self, bundle, **kwargs):
        #P '----obj_create------'
        repinUrl = '/api/v1/pin/'+bundle.data['repin']+'/'
        bundle = super(PinResource, self).obj_create(bundle, repinObj=repinUrl,  submitter=bundle.request.user, uImage=None, comments=[])
        messages.success(bundle.request, 'Your pin has been added.')
        mstore = messages.get_messages(bundle.request)
        for m in mstore:                  
            bundle.data['django_messages'] = [{"extra_tags": m.tags, "message": m, "level": m.level}]
        return bundle
        

    def obj_delete(self, bundle, **kwargs):
        if not hasattr(bundle.obj, 'delete'):
            try:
                bundle.obj = self.obj_get(bundle=bundle, **kwargs)
            except ObjectDoesNotExist:
                raise NotFound("A model instance matching the provided arguments could not be found.")
        if bundle.request.user == bundle.obj.submitter or bundle.request.user.is_superuser:
            self.authorized_delete_detail(self.get_object_list(bundle.request), bundle)
            bundle.obj.delete()
            #delete the images
            default_storage.delete(bundle.obj.image.name)
            default_storage.delete(bundle.obj.thumbnail.name)
            
            #TODO:try += so i dont accendnetly over write the bundle data.
            #TODO: how to add message to normal tasypie responce instead of forcing it here.  
            #Also, why is it not getting picked up by middleware, so i can gust use django messages.
            messages.success(bundle.request, 'Delete was successfull.')
            mstore = messages.get_messages(bundle.request)
            for m in mstore:                  
                bundle.data['django_messages'] = [{"extra_tags": m.tags, "message": m, "level": m.level}]
            #using HttpGone in stead of HttpNoContent so success message can be displaied.
            raise ImmediateHttpResponse(self.create_response(bundle.request, bundle, response_class = HttpGone))
        else:
            bundle.data = {"django_messages": [{"extra_tags": "alert alert-error fade-out", "message": 'You can not delete other users pins.', "level": 25}]}
            raise ImmediateHttpResponse(self.create_response(bundle.request, bundle, response_class = HttpForbidden))
        
        
class CmntResource(ModelResource):
    user = fields.ToOneField('pinry.api.api.UserResource', 'user', full=True)
    site_id = fields.CharField(attribute = 'site_id')
    content_object = GenericForeignKeyField({
        Pin: PinResource,
    }, 'content_object')
    validation = CleanedDataFormValidation(form_class=CommentForm)
    
    class Meta:
        always_return_data = True
        queryset = Comment.objects.all()
        resource_name = 'cmnt'
        include_resource_uri = False
        allowed_methods = ['get', 'post', 'put', 'delete']
        #fields, object_pk & content_type_id are REQUIRED for generic foreign key
        fields = ['id', 'comment', 'submit_date']
        #excludes = ["ip_address", "is_public", "is_removed", "user_email", "user_name", "user_url"]
        #other fields: "comment", "content_type_id", "id", "object_pk", "submit_date", "user_id", "username"

        filtering = {
            'object_pk': ALL_WITH_RELATIONS,
            'content_type': ALL_WITH_RELATIONS,
        }
        #authentication = BasicAuthentication()
        authorization = DjangoAuthorizationLimits()
    '''
    def dehydrate(self, bundle):
        #dehydrate follows for only favorites
        for f in bundle.data['follows'][:]:
            if f.data['id'] == None:
                bundle.data['follows'].remove(f)
        return bundle
    '''

    def alter_list_data_to_serialize(self, request, bundle):
        for obj in bundle['objects']:
            del obj.data['user'].data['email']
            del obj.data['user'].data['is_active']
            del obj.data['user'].data['is_staff']
            del obj.data['user'].data['is_superuser']
            del obj.data['user'].data['last_login']
            del obj.data['user'].data['last_name']
            del obj.data['user'].data['first_name']
            del obj.data['user'].data['date_joined']
            del obj.data['site_id']
            del obj.data['content_object']
            #del obj.data['object_pk']
            #del obj.data['content_type_id']
            
        return bundle
       
    def alter_detail_data_to_serialize(self, request, bundle):
        #del bundle.data['user']
        del bundle.data['site_id']
        del bundle.data['content_object']
        #DO NOT BLOCK THE BELOW. they need to be serialized for object creation with GFK!
        #del bundle.data['object_pk']
        #del bundle.data['content_type_id']
        return bundle

    def determine_format(self, request): 
        return "application/json" 
    
    def dehydrate_submit_date(self, bundle):
        return {'l':smartdate(bundle.obj.submit_date, 'long'), 's':smartdate(bundle.obj.submit_date, 'short'), 'd':smartdate(bundle.obj.submit_date, 'dot')}   
    
    def obj_create(self, bundle, **kwargs):
        #P '----obj_create------'
        #content_type='/api/v1/contrib/contenttype/'+bundle.data['content_type_id']+'/'
        #content_object_url = '/api/v1/pin/'+bundle.data['object_pk']+'/'
        
        # if id make sure the orig submitter remains in case of admin edit.
        id = bundle.data.get('id', None)
        if id:
            comment = Comment.objects.get(pk__exact=int(id))
            user = comment.user
        else:
            user = bundle.request.user
        bundle = super(CmntResource, self).obj_create(bundle, user=user)
        return bundle
        
class PinTagResource(ModelResource):

    class Meta:
        always_return_data = True
        queryset = Pin.tags.all()
        resource_name = 'pintags'
        include_resource_uri = False
        allowed_methods = ['get']
        fields = ['id', 'name']

        filtering = {
            'user': ALL_WITH_RELATIONS,
            'tags': ALL_WITH_RELATIONS,
        }
        authorization = DjangoAuthorizationLimits()
    
    def build_filters(self, filters=None):
        #P '---build filters---'
        if filters is None:
            filters = {}

        orm_filters = super(PinTagResource, self).build_filters(filters)
            
        if 'user' in filters and filters['user'] != 'null':
            orm_filters['pin__submitter__id__exact'] = filters['user']
            
        return orm_filters

    def determine_format(self, request): 
        return "application/json" 

    def dehydrate_tags(self, bundle):
        return map(str, bundle.obj.tags.all())