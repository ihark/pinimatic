from django.template.loader import render_to_string
from django.template import Library
from django.template import RequestContext

from pinry.pins.utils import getProfileContext


register = Library()


@register.simple_tag
def user_profile(request, profileId):
    context = getProfileContext(profileId)
    return render_to_string('pins/templatetags/user_profile.html',
        context,
        context_instance=RequestContext(request))
