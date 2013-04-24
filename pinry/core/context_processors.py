from django.conf import settings


def template_settings(request):
    return {'site_name': settings.SITE_NAME,}

def urls(request):
    """
    BASE_URL always refers to base site url.
    API_URL: http/https must be same as origin so use get_host
    """     
    return {'BASE_URL': settings.SITE_URL,
            'SSL_SITE_URL': settings.SSL_SITE_URL, 
            'API_URL': '//' + request.get_host() + '/api/' + settings.API_NAME + '/',
           }
    
def staticPrefix(request):
    """
    STATIC_PREFIX used to prepend full url to STATIC_URL when static files are hosted locally.
    use {{STATIC_PREFIX}}{{STATIC_URL}} for static items rendered outside base site context (bookmarklet)
    """     
    return {'STATIC_PREFIX': settings.STATIC_PREFIX,}

from urlparse import urlsplit
def redirects(request):
    referer = request.META.get('HTTP_REFERER', None)
    if referer:
        try:
            redirect_to = urlsplit(referer, 'http', False)[2]
        except IndexError:
            pass
    else:
        redirect_to = '{% url core:home %}'

    return {'HTTP_REFERER': redirect_to,}