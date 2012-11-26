from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .forms import PinForm
from .models import Pin

from django.utils import simplejson


def AjaxSubmit(request):
    #tests
    print '--- request recieved with obove reqest data ----'
    #end tests
    form = PinForm(request.GET, request.FILES)
    if request.user.is_authenticated():
        if form.is_valid():
            print '--- form is valid 0----'#
            pin = form.save(commit=False)
            print '--- form.save ----'#
            pin.submitter = request.user
            try:
                pin.save()
                form.save_m2m()
                print '--- form saved----'#
                messages.success(request, 'New pin successfully added.')
            except:
                messages.error(request, 'There was a issue with this image file. Note: .png & .gif. images are still buggy.')
    else:
        print '--- user did not pass authentication----'#
        messages.error(request, 'You are not loged in.', extra_tags='login')
    
    return HttpResponse( simplejson.dumps( form.errors ), mimetype='application/json' ) 
    

def recent_pins(request):
    return TemplateResponse(request, 'pins/recent_pins.html', None)

@login_required ()
def new_pin(request, pin_id=None):
    save = request.REQUEST.get('save', False)
    if pin_id:
        try:
            print 'view - pin id exists'
            pin = Pin.objects.get(pk=pin_id)
            form = PinForm(instance=pin)
            #id in hidden form filed bypasses duplicate url validation.
            form.fields['id'].initial = pin.pk
            #existing thumbmail displaied on form but not as form filed.
            thumbNail = ""#pin.thumbnail.url
            if pin.submitter != request.user:
                messages.error(request, 'This aint your pin!')            
        except Pin.DoesNotExist:
            messages.error(request, 'This pin does not exist.')
    else:
        print 'view - no pin id'
        pin = Pin()
        thumbNail = request.REQUEST['imgUrl']
        form = PinForm()
        
    if request.method == 'POST' or save:
        print 'view - enterd save mode'
        form = PinForm(request.REQUEST, request.FILES, instance=pin)
        if form.is_valid():
            pin = form.save(commit=False)
            if pin_id:
                print 'view - save mode - pin id exists'
                pin.edit()
            pin.submitter = request.user
            pin.save()
            form.save_m2m()
            if pin_id:
                messages.success(request, 'Pin successfully modified.')
            else:
                messages.success(request, 'New pin successfully added.')
            return HttpResponseRedirect(reverse('pins:recent-pins'))
        else:
            messages.error(request, 'Pin did not pass validation!')
    else:
        print 'not POST or Save'
        
    print 'form.instance = '+str(form.instance)
    #print all form fields for debugging
    for f in Pin._meta.fields:
        try:
            print 'pin.'+f.name+' = '+str(getattr(pin,f.name))
        except:
            print 'pin.'+f.name+' = does not exist'

    context = {
            'form': form,
            'thumbnail': thumbNail,
        }
    return TemplateResponse(request, 'pins/new_pin.html', context)


def delete_pin(request, pin_id=None):
    try:
        pin = Pin.objects.get(id=pin_id)
        if pin.submitter == request.user:
            pin.delete()
            messages.success(request, 'Pin successfully deleted.')
        else:
            messages.error(request, 'You are not the submitter and can not '
                                    'delete this pin.')
    except Pin.DoesNotExist:
        messages.error(request, 'Pin with the given id does not exist.')
        

    return HttpResponseRedirect(reverse('pins:recent-pins'))