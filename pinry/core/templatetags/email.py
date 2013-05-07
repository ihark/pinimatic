from django.template.loader import render_to_string
from django.template import Library, RequestContext, Context, loader
from pinry.pins.forms import PinForm


register = Library()


#@register.simple_tag
@register.inclusion_tag('email/templatetags/email_header_generic.html', takes_context=True)
def header_generic(context, request):
    print 'header_generic', context
    return context
    '''
    template = loader.get_template('email/templatetags/email_header_generic.html')
    return template.render(Context())
    '''
    '''
    return render_to_string('email/templatetags/email_header_generic.html',
        {'foo': 'bar'},
        context_instance=RequestContext(request))
    '''    