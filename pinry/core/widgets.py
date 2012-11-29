from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.utils.html import conditional_escape
from django.utils.encoding import force_unicode
from django.forms.widgets import ClearableFileInput, Input, CheckboxInput

class CustomImage(ClearableFileInput):

    def render(self, name, value, attrs=None):
        substitutions = {
            #uncomment to get 'Currently' 
            'initial_text': "", # self.initial_text, 
            'input_text': self.input_text,
            'clear_template': '',
            'clear_checkbox_label': self.clear_checkbox_label,
            }
        
        template = '%(input)s'
        substitutions['input'] = Input.render(self, name, value, attrs)

        if value and hasattr(value, "url"):
            template = u'%(initial_text)s %(initial)s %(clear_template)s<br />%(input_text)s: %(input)s'
            
            substitutions['initial'] = ('<img width="100px" src="%s" alt="%s"/>'
                                        % (escape(value.url),
                                           escape(force_unicode(value))))
            if not self.is_required:
                checkbox_name = self.clear_checkbox_name(name)
                checkbox_id = self.clear_checkbox_id(checkbox_name)
                substitutions['clear_checkbox_name'] = conditional_escape(checkbox_name)
                substitutions['clear_checkbox_id'] = conditional_escape(checkbox_id)
                substitutions['clear'] = CheckboxInput().render(checkbox_name, False, attrs={'id': checkbox_id})
                substitutions['clear_template'] = self.template_with_clear % substitutions

        return mark_safe(template % substitutions)

class CustomThumbnail(ClearableFileInput):

    def render(self, name, value, attrs=None):
        substitutions = {}
        
        template = ''
        

        if value and hasattr(value, "url"):
            template = u'%(initial)s'
            
            substitutions['initial'] = ('<img width="100px" src="%s" alt="%s"/>'
                                        % (escape(value.url),
                                           escape(force_unicode(value))))
            

        return mark_safe(template % substitutions)
#generates a thumnail icon with link to image
from django import forms
class AdminImageWidget(forms.FileInput):
    """
    A ImageField Widget for admin that shows a thumbnail.
    """

    def __init__(self, attrs={}):
        super(AdminImageWidget, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, "url"):
            output.append(('<a target="_blank" href="%s">'
                           '<img src="%s" style="height: 28px;" /></a> '
                           % (value.url, value.url)))
        output.append(super(AdminImageWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))