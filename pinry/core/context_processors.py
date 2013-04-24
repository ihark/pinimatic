from django.conf import settings
from pinry.core.utils import safe_base_url, safe_sbase_url, safe_usbase_url


def template_settings(request):
    return {'site_name': settings.SITE_NAME,}

def urls(request):
    """
    SITE_URL = base site url with automatic http/https.
    US_SITE_URL = http base site url
    SSL_SITE_URL = https base site url
    API_URL: http for now to avoid cross site requests if that is fixed
    then we can use auto http/https.
    """
    SITE_URL = safe_base_url(request)
    US_SITE_URL = safe_usbase_url(request)
    SSL_SITE_URL = safe_sbase_url(request)
  
    return {'BASE_URL': SITE_URL,
            'US_SITE_URL': US_SITE_URL, 
            'SSL_SITE_URL': SSL_SITE_URL, 
            'API_URL': US_SITE_URL + '/api/' + settings.API_NAME + '/',
           }
    
def staticPrefix(request):
    """
    STATIC_PREFIX prepends base url to STATIC_URL when in the development environment only!
    This must be use for all static files that will be rendered by the bookmarklet.
    Useage: {{STATIC_PREFIX}}{{STATIC_URL}}
    For Development server do not use full static url.
    Set STATIC_URL = '/static/'
    Set COMPRESS_URL = STATIC_URL
    """ 
    sp =  ''
    if not settings.RACK_ENV:
        sp = safe_base_url(request)
    return {'STATIC_PREFIX': sp,}

from urlparse import urlsplit
def redirects(request):
    """
    HTTP_REFERER: redirects to refering page
    """ 
    referer = request.META.get('HTTP_REFERER', None)
    if referer:
        try:
            redirect_to = urlsplit(referer, 'http', False)[2]
        except IndexError:
            pass
    else:
        redirect_to = '{% url core:home %}'

    return {'HTTP_REFERER': redirect_to,}