from django.template.loader import render_to_string
from django.template import Library
from django.template import RequestContext
from pinry.pins.forms import PinForm


register = Library()


@register.simple_tag
def new_pin(request):
    form = PinForm(user=request.user, initial={'next':request.get_full_path()})
    print '-------------',request.get_full_path()
    return render_to_string('pins/templatetags/new_pin.html',
        {'form': form},
        context_instance=RequestContext(request))
