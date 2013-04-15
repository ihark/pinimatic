from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.conf import settings
from django.template.loader import render_to_string
from django.template import RequestContext, loader
from django.contrib.auth.models import Group
from django.views.generic.simple import direct_to_template
from django.core.mail import send_mail
from .forms import ContactForm
#from django.contrib.admin.views.decorators import staff_member_required



def home(request):
    user = 'all'
    return HttpResponseRedirect(reverse('pins:recent-pins'))
    
def help(request):
    return TemplateResponse(request, 'core/help-bm.html')


def private(request):
    return TemplateResponse(request, 'core/private.html', None)

#not used switched to allauth
def register(request):
   
    if not settings.ALLOW_NEW_REGISTRATIONS:
        messages.error(request, "The admin of this service is not "
                                "allowing new registrations.")
        return HttpResponseRedirect(reverse('pins:recent-pins'))
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.groups.add(Group.objects.get(name=settings.DEFAULT_USER_GROUP))
            user.save()
            messages.success(request, 'Thank you for registering, you can now '
                                      'login.')
            return HttpResponseRedirect(reverse('core:login'))
    else:
        form = UserCreationForm()

    return TemplateResponse(request, 'core/register.html', {'form': form})

@login_required
def logout_user(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return HttpResponseRedirect(reverse('core:home'))

def bookmarklet(request):
    srcUrl = request.GET.get('srcUrl','')
    resp = render_to_string('bookmarklet/bookmarklet.js',context_instance=RequestContext(request, {
                                                                                "srcUrl": srcUrl,
                                                                                }))
    return HttpResponse(resp, mimetype="text/javascript")

@login_required
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            cc_myself = form.cleaned_data['cc_myself']
            #set where to send the contact email
            recipients = ['pinimatic@gmail.com']
            if cc_myself:
                recipients.append(sender)
            send_mail(subject, sender+"\n\n"+message, sender, recipients)
            return TemplateResponse(request, 'core/contact_thanks.html', {
                                                                'subject': subject,
                                                                'sender': sender,
                                                                }) 
    else:
        form = ContactForm()

    return TemplateResponse(request, 'core/contact.html', {'form': form})

def custom_500(request):
    t = loader.get_template('500.html')
    c = RequestContext(request, {'foo': 'bar'})
    return HttpResponse(t.render(c))
