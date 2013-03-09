from django.conf import settings


def template_settings(request):
    return {'site_name': settings.SITE_NAME,}

def baseUrl(request):
    """
    BASE_URL always refers to base site url.
    """     
    return {'BASE_URL': '//' + request.get_host(),}
    
def staticPrefix(request):
    """
    STATIC_PREFIX used to prepend full url to STATIC_URL when static files are hosted locally.
    use {{STATIC_PREFIX}}{{STATIC_URL}} for static items rendered outside base site context (bookmarklet)
    """     
    return {'STATIC_PREFIX': settings.STATIC_PREFIX,}