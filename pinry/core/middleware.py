from django.conf import settings
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django import http
from django.http import HttpResponse

import simplejson as json
from django.contrib import messages

from django.contrib.auth.middleware import RemoteUserMiddleware
#used to change default headder for remote user middleware
class CustomHeaderMiddleware(RemoteUserMiddleware):
    header = "HTTP_AUTHORIZATION"

class Public(object):
    def process_request(self, request):
        if settings.PUBLIC == False and not request.user.is_authenticated():
            acceptable_paths = [
                '/login/',
                '/private/',
                '/register/',
            ]
            if request.path not in acceptable_paths:
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
            response['Access-Control-Allow-Headers'] = 'Content-Type, X-CSRFToken, x-requested-with, authorization'
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
