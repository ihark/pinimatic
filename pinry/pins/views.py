from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from PIL import Image

from .forms import PinForm
from .models import Pin
from .utils import get_top_domains
from django.contrib.auth.models import User

from django.utils import simplejson
from django.conf import settings
from django.core.files.storage import default_storage

from follow.models import Follow
from django.db.models import Count
from django.contrib.sites.models import get_current_site
from django.contrib.comments.models import Comment
from ..core.utils import redirect_to_referer


def AjaxSubmit(request):
    form = PinForm(request.GET, request.FILES)
    if request.user.is_authenticated():
        if form.is_valid():
            pin = form.save(commit=False)
            pin.uImage = form.cleaned_data['uImage']
            pin.submitter = request.user
            try:
                pin.save()
                form.save_m2m()
                messages.success(request, 'New pin successfully added.')
            except:
                messages.error(request, 'Oops! Somthing went wrong while saving this pin.')
    else:
        messages.error(request, 'Please log in to submit this item.', extra_tags='login')
    return HttpResponse( simplejson.dumps( form.errors ), mimetype='application/json' ) 
    

def recent_pins(request):
    pins = Pin.objects.all()
    #create dictionary of srcUrls striped to domain > convert to sorted list > put top 5 in srcDoms
    srcUrls = pins.order_by('srcUrl').values_list('srcUrl').annotate(count=Count('srcUrl'))
    srcDoms = get_top_domains(srcUrls, 5)
    tags = pins.order_by('tags__name').values_list('tags__name').annotate(count=Count('tags__name'))
    tags = tags[:20]
    context = {
            'srcDoms': srcDoms,
            'tags': tags,
        }

    return TemplateResponse(request, 'pins/recent_pins.html', context)

def pin_detail(request, pinId):
    pin = Pin.objects.get(id=pinId)
    profileId = pin.submitter.id
    
    context = {
            'profileId':profileId,
            'pinId':pinId,
        }

    return TemplateResponse(request, 'pins/pin_detail.html', context)
    
def user_profile(request, profileId=None, tag=None):
    #provide profileId for user_profile templatetag
    #profile gets its context from pins.utils getProfileContext()
    context = {'profileId':profileId}

    return TemplateResponse(request, 'pins/user_profile.html', context)

#create new pin or edit exitsing pin, based on presence of id.
@login_required ()
def new_pin(request, pin_id=None):
    save = request.REQUEST.get('save', False)
    thumb = None
    if pin_id:
        try:
            pin = Pin.objects.get(pk=pin_id)
            form = PinForm(instance=pin, user=request.user)
            form = redirect_to_referer(request, form)
            #show existing thumbmail on edit form.
            thumb = pin.thumbnail.url
            if not request.user.is_superuser and pin.submitter != request.user:
                messages.error(request, 'You can not edit other users pins x.')
                redirect_to = redirect_to_referer(request)
                return HttpResponseRedirect(redirect_to)
        except Pin.DoesNotExist:
            messages.error(request, 'This pin does not exist.')
    else:
        pin = Pin()
        if not request.method == 'POST' or save:
            form = PinForm(user=request.user)
            form = redirect_to_referer(request, form)
        
    if request.method == 'POST' or save:
        #print 'view - enterd save mode'
        form = PinForm(request.REQUEST, request.FILES, instance=pin)
        # request.FILES is for file uploader 
        #TODO: do i need request.REQUEST?
        """
        #print all form fields for debugging
        print 'request.FILES:',request.FILES
        print 'form.instance = '+str(form.instance.id)
        print form.data
        for f in form:
            try:
                print f.name+' = '+form.data[f.name]
            except:
                print f.name+' = does not exist'
        #end debug
        """
        if form.is_valid():
            #print 'form is valid'
            pin = form.save(commit=False)
            pin.uImage = form.cleaned_data['uImage']
            if pin_id:
                #print 'view - save mode - pin id exists'
                pin.edit()
            else:
                pin.submitter = request.user
            #print 'view - pin.save()'
            pin.save()
            #print 'view - form.save_m2m()'
            form.save_m2m()
            redirect_to = redirect_to_referer(request, form)
            if pin_id:
                messages.success(request, 'Pin successfully modified.')
                return HttpResponseRedirect(redirect_to)
            else:
                messages.success(request, 'New pin successfully added.')
                return HttpResponseRedirect(redirect_to)
            
        else:
            messages.error(request, 'Pin did not pass validation!')
            if form.is_bound:
                if form.saved_data['uImage']:
                    #(only comes into play on image upload with form error on resubmit)
                    #this makes thumnail for image uplaod
                    thumb = settings.TMP_URL+form.saved_data['uImage']
                    #form.saved_data is = form.cleaned_data for invalid forms
                    form = PinForm(form.saved_data)
                else:
                    #print 'view - url submitted for thumb'
                    thumb = request.REQUEST['imgUrl']
                    #print 'view - edit invalid form'
    else:
        pass
        #print 'view - not POST or Save'
    if not thumb:
        thumb = '/static/core/img/thumb-default.png'
    context = {
            #'tempImg': tempImg
            'form': form,
            'thumb': thumb,
        }
    return TemplateResponse(request, 'pins/new_pin.html', context)


def delete_pin(request, pin_id=None):
    try:
        pin = Pin.objects.get(id=pin_id)
        if pin.submitter == request.user or request.user.is_superuser:
            default_storage.delete(pin.image.name)
            default_storage.delete(pin.thumbnail.name)
            pin.delete()

            messages.success(request, 'Pin successfully deleted.')
        else:
            messages.error(request, 'You can not delete other users pins.')
    except Pin.DoesNotExist:
        messages.error(request, 'Pin with the given id does not exist.')

    return HttpResponseRedirect(session_next(request))

#TODO: This needs to be setup. Currently using api only.
def comment(request, pk=1):
    pin = Pin.objects.get(pk__exact=pk)
    
    #if current_site.domain == 'foo.com':
    context = {
            'pin': pin
        }
    return TemplateResponse(request, 'pins/comments/comment.html', context)
  