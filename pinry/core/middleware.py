from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django import http
from django.http import HttpResponse

import simplejson as json
from django.contrib import messages
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.http import HttpResponsePermanentRedirect

#used to change default headder for remote user middleware
class CustomHeaderMiddleware(RemoteUserMiddleware):
    header = "HTTP_AUTHORIZATION"

class Public(object):
    def __init__(self):
        self.acceptable_paths = [
                #'/accounts/login/',
                '/private/',
            ]
        self.acceptable_domains = (
                '/accounts/',
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
                    return HttpResponseRedirect(settings.SITE_URL+reverse('core:private'))
                
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
        response['P3P'] = 'CP="NOI OUR NID PSA"'#getattr(settings, 'P3P_COMPACT', None)
        return response

#Require SSL for SECURE_REQUIRED_PATHS if HTTPS_SUPPORT=true
class SecureRequiredMiddleware(object):
    def __init__(self):
        self.paths = getattr(settings, 'SECURE_REQUIRED_PATHS', False)
        self.enabled = self.paths and getattr(settings, 'HTTPS_SUPPORT', False)
        self.dev_https_port = getattr(settings, 'HTTPS_DEV_PORT', False)

    def _is_secure(self, request):
        if request.is_secure():
            return True
        #Handle the Webfaction case until this gets resolved in the request.is_secure() 
        if 'HTTP_X_FORWARDED_SSL' in request.META:
            return request.META['HTTP_X_FORWARDED_SSL'] == 'on'
        #Handle the Heroku case until this gets resolved in the request.is_secure() 
        if 'HTTP_X_FORWARDED_PROTO' in request.META:
            print request
            print '-----------'+request.META['HTTP_X_FORWARDED_PROTO']
            return request.META['HTTP_X_FORWARDED_PROTO'] == 'https'
        #Development server case
        if self.dev_https_port:
            eval = request.META['HTTP_HOST'].split(':')[-1] == self.dev_https_port
            print 'middleware:  is_secture test: ', eval
            return eval
        return False
        
    def is_secure_path(self, request):
        secure =  False
        for path in self.paths:
            if request.get_full_path().startswith(path):
                secure =  True
        return secure

    def process_request(self, request):
        if self.enabled:
            print 'middleware: SecureRequired'
            request_path = request.get_full_path()
            request_url = request.build_absolute_uri(request_path)
            server_port = request.META['SERVER_PORT']
            request_port = request.META['HTTP_HOST'].split(':')[-1]
            print 'middleware: --cheking request url: ', request_url
            print 'middleware: --is_secure_path: ', self.is_secure_path(request)
            print 'middleware: --request_is_secure: ', self._is_secure(request)
            if self.is_secure_path(request) and not self._is_secure(request):
                secure_url = request_url.replace('http://', 'https://')
                #DEVELOPMENT SEVER: Change port to dev_https_port
                if self.dev_https_port:
                    secure_url = secure_url.replace(server_port, self.dev_https_port)
                print 'middleware: --redirecting to https'
                return HttpResponsePermanentRedirect(secure_url)
            if not self.is_secure_path(request) and self._is_secure(request):
                unsecure_url = request_url.replace('https://', 'http://')
                #DEVELOPMENT SEVER: Change port to serverport
                if self.dev_https_port:
                    unsecure_url = unsecure_url.replace(self.dev_https_port, server_port)
                print 'middleware: --redirecting to http'
                return HttpResponsePermanentRedirect(unsecure_url)
            print 'middleware: --no redirect required'
        return None
