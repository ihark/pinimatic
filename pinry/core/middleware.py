from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django import http
from django.http import HttpResponse

import simplejson as json
from django.contrib import messages
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.http import HttpResponsePermanentRedirect
import re

#used to change default headder for remote user middleware
class CustomHeaderMiddleware(RemoteUserMiddleware):
    header = "HTTP_AUTHORIZATION"

class DevHttpsMiddleware:
    """
    Adds support for SECURE_PROXY_SSL_HEADER on django's development server for proper https handling.
    Settings:
        - HTTPS_SUPPORT (=False): Set True to enable SSL & this middleware.
        - HTTPS_DEV_PORT (=None): Specify HTTPS port used for django's development server 
          (requires stunnel or similar).
        - SECURE_PROXY_SSL_HEADER (=None): Set to a tuple with the header name and value to set when https
          ie:('HTTP_X_FORWARDED_PROTO', 'https')
          * WARNING: If the headder specified in SECURE_PROXY_SSL_HEADER is not supported on your production 
          server you must limit this settings value to the developemnt environment ONLY!!!!
        - RACK_ENV (=False): Your settings should be configured to detect RACK_ENV on production servers only! 
          ie: RACK_ENV = os.environ.get("RACK_ENV", False)
    Install Notes: This middleware must be added to the top of your installed middleware.
    """
    def __init__(self):
        self.enabled = getattr(settings, 'HTTPS_SUPPORT', False)
        self.dev_https_port = getattr(settings, 'HTTPS_DEV_PORT', None)
        self.secure_header = getattr(settings, 'SECURE_PROXY_SSL_HEADER', None)
        self.production = getattr(settings, 'RACK_ENV', False)

    def process_request(self, request):
        if self.enabled and not self.production:
            host = request.get_host()
            if host.split(':')[-1] ==  self.dev_https_port and self.secure_header:
                request.META[self.secure_header[0]] = self.secure_header[1]
                request_path = request.get_full_path()
                #secure_url = request.build_absolute_uri(request_path)
                print '***DevHttpsMiddleware made secure: ',request_path
    
class SecureRequiredMiddleware(object):
    """
    Forces to HTTPS or HTTP by path(s) specified:
        
    Settings:
        - HTTPS_SUPPORT (=False): Set True to enable SSL.
        - HTTPS_DEV_PORT (=None): Specify HTTPS port used for django's development server 
          requires stunnel or similar).
        - SECURE_REQUIRED_PATHS (=None): Specify paths as '/path/' to force https, all other 
          paths will be forced to http.
        - SECURE_IGNORED_PATHS (=None): Specify paths to ignore, will reamain as requested.

    Install Notes:
        - DevHttpsMiddleware is requered for HTTPS support on django's development server & this middleware 
        - Must be installed below DevHttpsMiddleware.
    """
    def __init__(self):
        self.paths = getattr(settings, 'SECURE_REQUIRED_PATHS', None)
        self.paths_ignored = getattr(settings, 'SECURE_IGNORED_PATHS', None)
        self.enabled = self.paths and getattr(settings, 'HTTPS_SUPPORT', False)
        self.dev_https_port = getattr(settings, 'HTTPS_DEV_PORT', None)
    
    def is_secure_path(self, request):
        secure =  False
        for path in self.paths:
            if request.get_full_path().startswith(path):
                secure =  True
        return secure
    
    def is_ignored_path(self, request):
        ignored =  False
        for path in self.paths_ignored:
            if request.get_full_path().startswith(path):
                ignored =  True
        return ignored
    
    def process_request(self, request):
        #ajax requests must be excluded from redirects.
        referer = request.META.get('HTTP_REFERER', False)
        post = request.method == 'POST' or request.REQUEST.get('save', False)
        if not post and referer and self.enabled and not request.is_ajax() and not self.is_ignored_path(request):
            #print '----middleware: SecureRequired----'
            request_path = request.get_full_path()
            request_url = request.build_absolute_uri(request_path)
            print '***secure requered - request_url: ',request_url
            print '***secure requered - request.is_secure(): ',request.is_secure()
            server_port = request.META['SERVER_PORT']
            request_port = request.META['HTTP_HOST'].split(':')[-1]
            #print 'middleware: --cheking request url: ', request_url
            #print 'middleware: --secure_required: ', self.is_secure_path(request)
            #print 'middleware: --requestis_secure: ', request.is_secure()
            
            #Redirect to https if designated as a secure path
            if self.is_secure_path(request) and not request.is_secure():
                secure_url = request_url.replace('http://', 'https://')
                #DEVELOPMENT SEVER: Change port to dev_https_port
                if self.dev_https_port:
                    secure_url = secure_url.replace(server_port, self.dev_https_port)
                print '+++++++middleware+++++++ redirecting to https: ', secure_url
                return HttpResponsePermanentRedirect(secure_url)
            
            #Redirect to http if NOT designated as a secure path
            if not self.is_secure_path(request) and request.is_secure():
                unsecure_url = request_url.replace('https://', 'http://')
                #DEVELOPMENT SEVER: Change port to serverport
                if self.dev_https_port:
                    unsecure_url = unsecure_url.replace(self.dev_https_port, server_port)
                print '+++++++middleware+++++++ redirecting to http: ', unsecure_url
                print '----ssl method', request.method
                print '----ssl REQUEST', request.REQUEST
                return HttpResponsePermanentRedirect(unsecure_url)
            #print 'middleware: --no redirect required'
        return None
    
class Public(object):
    """
    Adds private support to the aplication.
    Instal Notes: This middleware must be installed below DevHttpsMiddleware & SecureRequiredMiddleware.
    """
    def __init__(self):
        self.acceptable_paths = [
                '/private/',
                '/ajax/submit/',
                reverse('pins:new-pin'),
            ]
        self.acceptable_domains = (
                '/accounts/',
                '/bookmarklet/',
                '/api/',
                '/static/',
                r'/favicon',
            )
    
    def is_acceptable_domain(self, request):
        acceptable =  False
        for path in self.acceptable_domains:
            if request.get_full_path().startswith(path):
                acceptable =  True
        return acceptable
    
    def process_request(self, request):
        if settings.PUBLIC == False and not request.user.is_authenticated():
            if request.path not in self.acceptable_paths:
                if not self.is_acceptable_domain(request):
                    print '+++++++middleware+++++++  redirected to private: ',request.path 
                    #return HttpResponseRedirect(safe_reverse(request,'core:private'))
                    return HttpResponseRedirect(reverse('core:private'))
                
# used for cors, sets allowed orign to request orign because * not allowed
class AllowOriginMiddleware(object):
    def process_request(self, request):
        if request.method == 'OPTIONS':
            return HttpResponse()


    def process_response(self, request, response):
        origin = request.META.get('HTTP_ORIGIN')
        if origin:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, DELETE, PUT'
            response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken, x-requested-with, authorization, cache-control'
            response['Access-Control-Allow-Credentials'] = 'true'
        return response

from django.contrib import messages
#enables django messages & form errors to be used with ajax requests
class AjaxMessaging(object):
    def process_response(self, request, response):
        if request.is_ajax():
            if response['Content-Type'] in ["application/javascript", "application/json"]:
                try:
                    content = json.loads(response.content)
                    #format form.errors
                    for key in content:
                        content[key][0] = {"message":content[key][0]}
                        content[key][0].update({
                        "level":"form field error",
                        "extra_tags":"form field error",
                        })
                        if key == '__all__':
                            content[key][0].update({
                        "level":"form error",
                        "extra_tags":"alert alert-error",
                        })
                            
                except ValueError:
                    print '-----AjaxMessaging-----ValueError:'
                    print ValueError
                    
                    return response

                django_messages = []
                #format django messages
                for message in messages.get_messages(request):
                    django_messages.append({
                        "message": message.message,
                        "level": message.level,
                        "extra_tags": message.tags,
                    })

                content['django_messages'] = django_messages

                response.content = json.dumps(content)
        return response

#Required for ie to send our cookies via the bookmarklet
class P3PHeaderMiddleware(object):
    def process_response(self, request, response):
        response['P3P'] = getattr(settings, 'P3P_COMPACT', None)
        return response

#NOT USED: works well but dont want next to carry over between windows....
#using redirect_to_referrer utility instead.
from urlparse import urlsplit
class SessionNextMiddleware(object):
    """
    Easy redirection to refering page:
    Insures that request.session['next'] always contains the refering page for redirection ny
    The refering path is added to session['next'] upon navigation and locks session['next'] during 
    form validation. It becomes unloced when navigating away from the from or after a successfull submit.
    There is a bypass for modal forms so that you are redirected to the originating page.
    SETUP form template: (requires install: core.context_processors.redirects)
    Cancil button: <a href="{{SESSION_NEXT}}">Cancel</a>
    SETUP (from tempate, if modal):
    action="{% url your_view %}?modal=True"
    SETUP (form view):
    from core.utils import session_next
    return HttpResponseRedirect(session_next(request))
    """
    def process_request(self, request):
        referer = request.META.get('HTTP_REFERER', None)
        request_path = request.get_full_path()
        modal = request.REQUEST.get('modal', False)
        if modal and referer:
            us = urlsplit(referer)
            request.session['next'] = us.path
            us = urlsplit(request_path)
            return HttpResponseRedirect(us.path)
        if not modal and referer and request_path.split('/')[1] not in ['api', 'media', 'ajax']:
            us = urlsplit(referer)
            referer = us.path
            save = request.REQUEST.get('save', False)
            session_next = request.session.get('next',None)
            next_locked = request.session.get('next_locked', None)        
            if next_locked == None:
                request.session['next_locked'] = False
            if session_next == None:
                request.session['next'] = reverse('core:home')
            if request_path != request.session['next_locked']:
                request.session['next_locked'] = False
            if referer and request.method == 'POST' or save:
                    request.session['next_locked'] = request_path
            if not request.session['next_locked']:
                    request.session['next'] = referer
        return None
