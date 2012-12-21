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

from django.utils import simplejson
from pinry.settings import SITE_URL, TMP_URL
from django.core.files.storage import default_storage


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
                messages.error(request, 'There was a issue with this image file. Note: .png & .gif. images are still buggy.')
    else:
        print '--- user did not pass authentication----'#
        messages.error(request, 'You are not loged in.', extra_tags='login')
    
    return HttpResponse( simplejson.dumps( form.errors ), mimetype='application/json' ) 
    

def recent_pins(request):
    return TemplateResponse(request, 'pins/recent_pins.html', None)

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
                #this makes thumnail for image uplaod
                #(only comes into play on image upload with form error on resubmit)
                print 'view - image submitted for thumb saveTempImg() called'
                thumb = SITE_URL+TMP_URL+form.saved_data['uImage']
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
            default_storage.delete(pin.image.path)
            default_storage.delete(pin.thumbnail.path)
            pin.delete()

            messages.success(request, 'Pin successfully deleted.')
        else:
            messages.error(request, 'You can not delete other users pins.')
    except Pin.DoesNotExist:
        messages.error(request, 'Pin with the given id does not exist.')
        

    return HttpResponseRedirect(reverse('pins:recent-pins'))