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
from django.middleware.csrf import get_token
from django.views.decorators.csrf import requires_csrf_token
from pinry.api.api import UserResource
from ..core.utils import redirect_to_referer
from django.contrib.auth.decorators import login_required
from follow.models import Follow
#from django.contrib.admin.views.decorators import staff_member_required



def home(request):
    user = 'all'
    return HttpResponseRedirect(reverse('pins:recent-pins'))
    
def help(request):
    return TemplateResponse(request, 'core/help-bm.html')


def private(request):
    return TemplateResponse(request, 'core/private.html', None)

def logged_out(request):
    messages.info(request, "Thank you for participating in our pre-beta test! Let us know if there is anyting we can do to make things better.  \
                            New features are constatly being rolled out so check back often for more great stuff.")
    return HttpResponseRedirect(reverse('core:home'))
    

@requires_csrf_token 
def bookmarklet(request):
    srcUrl = request.GET.get('srcUrl','')
    ur = UserResource()
    user = request.user
    if request.is_secure() or not settings.RACK_ENV:
        #return user object for javascript (ID does not authenticate)
        if request.user.is_authenticated():
            user = ur.obj_get(id=user.id, bundle=ur.build_bundle(request=request)) 
            ur_bundle = ur.build_bundle(obj=user, request=request)
            auth_user_o = ur.full_dehydrate(ur_bundle)
            auth_user_o = ur.serialize(None, auth_user_o, 'application/json')
        else:
            auth_user_o = "null"
        #this is a way to get csrf token into IE via bookmarklet
        #csrftoken = get_token(request)
        csrftoken = "null"

        resp = render_to_string('bookmarklet/bookmarklet.js',context_instance=RequestContext(request, {
                                                                                    "srcUrl": srcUrl,
                                                                                    "auth_user_o": auth_user_o,
                                                                                    "csrftoken" : csrftoken,
                                                                                    }))
        #.set_cookie(settings.SECRET_KEY, value='csrftoken', max_age=None, expires=None, path='/', domain=None, secure=None, httponly=False)   
        return HttpResponse(resp, mimetype="text/javascript")
    else:
        return HttpResponse("javascript :alert('Please go to pinimatic.herokuapp.com and install the new bookmarlet.  We apologise for any inconvenience.');")
    

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            cc_myself = form.cleaned_data['cc_myself']
            #where the email gets sent!
            recipients = ['pinimatic@gmail.com']
            if cc_myself:
                recipients.append(sender)
            send_mail(subject, sender+"\n\n"+message, sender, recipients)
            #TODO: These messages should be click or swipe to close...
            if subject == 'Feedback':
                messages.info(request, "Thanks for the feedback!")
            if subject == 'Bugs':
                messages.info(request, "Thanks for the bug report!")
            if subject == 'Support':
                messages.info(request, "Thanks for contacting the support team.\
                                          We'll get back to you with some answers \
                                          as soon as we can!")
            redirect_to = redirect_to_referer(request, form)
            return HttpResponseRedirect(redirect_to)
            #TODO: clean up unused templates and put full messages in view.
            """return TemplateResponse(request, 'core/contact_thanks.html', {
                                                                'subject': subject,
                                                                'sender': sender,
                                                                })"""
            
    else:
        if request.user.is_authenticated():
            sender = request.user.email
        else:
            sender = ''
        form = ContactForm(initial={ 'sender': sender, 'cc_myself': True})
        form = redirect_to_referer(request, form)
    return TemplateResponse(request, 'core/contact.html', {'form': form})

def custom_500(request):
    t = loader.get_template('500.html')
    c = RequestContext(request, {'foo': 'bar'})
    return HttpResponse(t.render(c))

from pinry.pins.utils import getProfileContext, get_relationships
from pinry.pins.models import Pin
def relationships(request):
    user = request.user
    profileId = user.id
    
    context = {
            'profileId':profileId,
        }
        
    #get relationships
    context.update(getProfileContext(profileId))#this may not be needed in template
    following = context.get('following', None)
    followers = context.get('followers', None)
    relationships = get_relationships(user, following, followers)
    context.update({'relationships':relationships})
    #get pin thumbs for all related users
    if relationships:
        for type in relationships:
            for user in relationships[type]:
                pins = Pin.objects.filter(submitter__exact=user)[:20]
                user.pins = pins

    return TemplateResponse(request, 'core/relationships.html', context)

from django.db.models.loading import cache
@login_required
def unfollow(request, app, model, id, user_id=None):
    if not user_id:
        user_id = request.user.id
    model = cache.get_model(app, model)
    obj = model.objects.get(pk=id)
    follow = Follow.objects.get_follows(obj).get(user__id=user_id)
    if follow.user == request.user or follow.folowing == request.user:
        follow.delete()
    redirect_to = redirect_to_referer(request)
    return HttpResponseRedirect(redirect_to)
    
@login_required
def unfollow_by_id(request, follow_id):
    follow =  Follow.objects.get(id=follow_id)
    if follow.user == request.user or follow.folowing == request.user:
        follow.delete()
        redirect_to = redirect_to_referer(request)
    return HttpResponseRedirect(redirect_to)