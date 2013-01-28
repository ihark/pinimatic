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
from django.contrib.auth.models import User

from django.utils import simplejson
from django.conf import settings
from django.core.files.storage import default_storage

from follow.models import Follow
from django.db.models import Count
from urlparse import urlparse, urlunparse


def AjaxSubmit(request):
    #tests
    print '--- request recieved with obove reqest data ----'
    #end tests
    form = PinForm(request.GET, request.FILES)
    if request.user.is_authenticated():
        if form.is_valid():
            print '--- ajax form is valid ----'#
            pin = form.save(commit=False)
            pin.uImage = form.cleaned_data['uImage']
            pin.submitter = request.user
            try:
                print '--- ajax try form.save ----'#
                pin.save()
                print '--- ajax form.saved ----'#
                form.save_m2m()
                print '--- ajax M2M form saved----'#
                messages.success(request, 'New pin successfully added.')
            except:
                messages.error(request, 'Oops! Somthing went wrong while saving this pin.')
    else:
        print '--- user did not pass authentication----'#
        messages.error(request, 'You are not loged in.', extra_tags='login')
    
    return HttpResponse( simplejson.dumps( form.errors ), mimetype='application/json' ) 
    

def recent_pins(request):
    return TemplateResponse(request, 'pins/recent_pins.html', None)
    
def user_profile(request, profileName=None, tag=None):
    profile = User.objects.get(username__exact=profileName)
    pins = Pin.objects.filter(submitter=profile)
    pinsC = pins.count()
    tags = pins.order_by('tags__name').filter(submitter=profile).values_list('tags__name').annotate(count=Count('tags__name'))
    tagsC = tags.distinct().count()
    folowers = Follow.objects.get_follows(profile).values_list('user__username', flat=True)
    folowersC = folowers.count()
    folowing = Follow.objects.filter(user=profile).exclude(folowing__exact=None).values_list('folowing__username', flat=True)
    folowingC = folowing.count()
    favs = Follow.objects.filter(user=profile).exclude(favorite__exact=None).values_list('favorite__pk', flat=True)
    favsC = favs.count()
    #create dictionary of srcUrls striped to domain > convert to sorted list > put top 5 in srcDoms
    srcUrls = pins.order_by('srcUrl').values_list('srcUrl').annotate(count=Count('srcUrl'))
    srcDomains = {}
    for url in srcUrls:
        p = urlparse(url[0])
        dom = p.netloc
        count = url[1]
        parts = p.scheme, p.netloc, '', '', '', ''
        url = urlunparse(parts)
        if dom not in srcDomains and dom != '':
            srcDomains[dom] = count, url
        elif dom != '':
            srcDomains[dom] = srcDomains[dom][0]+count, url
    print srcDomains
    import operator
    srcDomains = sorted(srcDomains.iteritems(), key=operator.itemgetter(1), reverse=True)
    srcDoms =srcDomains[:5]
    
    print pinsC
    print tags
    print tagsC
    print folowers
    print folowersC
    print folowing
    print folowingC
    print favs
    print favsC
    print srcDoms

    
    context = {
            'profile': profile,
            'pinsC': pinsC,
            'folowers': folowers,
            'folowersC': folowersC,
            'folowing': folowing,
            'folowingC': folowingC,
            'tags': tags,
            'tagsC': tagsC,
            'favs': favs,
            'favsC': favsC,
            'srcDoms': srcDoms,
        }
    return TemplateResponse(request, 'pins/user_profile.html', context)

#create new pin or edit exitsing pin, based on presence of id.
@login_required ()
def new_pin(request, pin_id=None):
    save = request.REQUEST.get('save', False)
    if pin_id:
        try:
            print 'view - edit pin - pin id exists'
            pin = Pin.objects.get(pk=pin_id)
            form = PinForm(instance=pin)
            #show existing thumbmail on edit form.
            thumb = pin.thumbnail.url
            if pin.submitter != request.user:
                messages.error(request, 'You can not edit other users pins.')  
                return HttpResponseRedirect(reverse('pins:recent-pins'))
        except Pin.DoesNotExist:
            messages.error(request, 'This pin does not exist.')
    else:
        print 'view - new pin - no pin id'
        pin = Pin()
        form = PinForm()
        thumb = '/static/core/img/thumb-default.png'
        
    if request.method == 'POST' or save:
        print 'view - enterd save mode'
        form = PinForm(request.REQUEST, request.FILES, instance=pin)
        print request.FILES
        #print all form fields for debugging
        print 'form.instance = '+str(form.instance.id)
        print form.data
        for f in form:
            try:
                print f.name+' = '+form.data[f.name]
            except:
                print f.name+' = does not exist'
        #end debug
        if form.is_valid():
            print 'form is valid'
            pin = form.save(commit=False)
            pin.uImage = form.cleaned_data['uImage']
            pin.submitter = request.user
            if pin_id:
                print 'view - save mode - pin id exists'
                pin.edit()
            pin.save()
            form.save_m2m()
            if pin_id:
                messages.success(request, 'Pin successfully modified.')
            else:
                messages.success(request, 'New pin successfully added.')
                return HttpResponseRedirect(reverse('pins:recent-pins'))
            
        else:
            messages.error(request, 'Pin did not pass validation!')
            if form.is_bound:
                if form.saved_data['uImage']:
                    #(only comes into play on image upload with form error on resubmit)
                    print 'view - getting thumb & data for error corection form'
                    #this makes thumnail for image uplaod
                    thumb = settings.TMP_URL+form.saved_data['uImage']
                    #form.saved_data is = form.cleaned_data for invalid forms
                    form = PinForm(form.saved_data)
                else:
                    print 'view - url submitted for thumb'
                    thumb = request.REQUEST['imgUrl']
                    print 'view - edit invalid form'
    else:
        print 'not POST or Save'
        
    context = {
            #'tempImg': tempImg
            'form': form,
            'thumb': thumb,
        }
    return TemplateResponse(request, 'pins/new_pin.html', context)


def delete_pin(request, pin_id=None):
    try:
        pin = Pin.objects.get(id=pin_id)
        if pin.submitter == request.user:
            default_storage.delete(pin.image.name)
            default_storage.delete(pin.thumbnail.name)
            pin.delete()

            messages.success(request, 'Pin successfully deleted.')
        else:
            messages.error(request, 'You can not delete other users pins.')
    except Pin.DoesNotExist:
        messages.error(request, 'Pin with the given id does not exist.')
        
    print request
    return HttpResponseRedirect(reverse('pins:recent-pins'))