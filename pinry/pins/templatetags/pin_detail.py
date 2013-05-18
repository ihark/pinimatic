from django.template.loader import render_to_string
from django.template import Library
from django.template import RequestContext

from pinry.pins.utils import getPinContext


register = Library()


@register.simple_tag
def pin_detail(request, pinId):
    context = getPinContext(request, pinId)
    return render_to_string('pins/templatetags/pin_detail.html',
        context,
        context_instance=RequestContext(request))
