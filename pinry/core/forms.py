from taggit.forms import TagField, TagWidget
from django.forms.widgets import SelectMultiple, Textarea, HiddenInput, TextInput
from django import forms
from django.utils.translation import ugettext as _
from taggit.utils import parse_tags, edit_string_for_tags
import re

from django import forms

class ContactForm(forms.Form):
    SUBJECTS = (
        ('Feedback', 'Feedback'),
        ('Bugs', 'Bug Report'),
        ('Support', 'Support'),
    )
    subject = forms.ChoiceField(choices=SUBJECTS)
    message = forms.CharField(widget=Textarea(attrs={'placeholder':'Enter your message here'}))
    sender = forms.EmailField(label='Your Email', widget=TextInput(attrs={'placeholder':'email@example.com'}))
    cc_myself = forms.BooleanField(required=False)
    next = forms.CharField(widget=HiddenInput())
    honey = forms.CharField(required=False, label='', widget=TextInput(attrs={'style':'display: none;'}))

    def __init__(self, *args, **kwargs):
        super(forms.Form, self).__init__(*args, **kwargs)
        
    def clean_honey(self):
        #P '--form clean_repin'
        data = self.cleaned_data['honey']
        if data == '':
            pass
        else:
            raise forms.ValidationError("You must be a robot!")
        return data    
        
class CustomTagWidget(forms.TextInput):
    def render(self, name, value, attrs=None):
        attrs={'placeholder':'add new tags here'}
        print 'TODO: core.models.CustomTagWidget move to widget file'
        #P "widget attrs", attrs
        #P "widget value",value
        #P "widget name",name
        if value is not None and not isinstance(value, basestring):
            value = edit_string_for_tags([o.tag for o in value.select_related("tag")])
            #remove all quotes from tag values when rendered on form
            value = re.sub(r'"', '', value)
            #value = ""#remove exising values from form
        return super(CustomTagWidget, self).render(name, value, attrs)

from pinry.core.utils import format_tags, format_tags_list
class CustomTagField(forms.CharField):
    widget = CustomTagWidget
    def clean(self, value):
        value = super(CustomTagField, self).clean(value)
        print 'TODO: core.models.CustomTagField move to widget file'
        if value:
            try:
                #jquery.tagit compatability: make sure there is a comma if not present.
                #This allows one mutiword tag, jquery.tagit does not put a comma after  
                #first tag if no second tag and django-taggit will use spaces if no comma.
                if not value.find(',')+1:
                    value = value+','
                    print value
                return parse_tags(value)
            except ValueError:
                print '****CustomTagField ValueError'
                raise forms.ValidationError("Provide one or more comma-separated tags.")
        else: 
            return value

class UserTagsWidget(forms.CheckboxSelectMultiple):
    def render(self, name, value, attrs=None):
        print 'TODO: core.models.UserTagsWidget move to widget file'
        #make sure there is only one of each tag in choices
        seen = set()
        seen_add = seen.add
        choices = [ x for x in self.choices if x not in seen and not seen_add(x)]
        self.choices = choices
        #P self.choices
        #for c in self.choices: print 'choices:', c
        
        return super(UserTagsWidget, self).render(name, value, attrs)

class UserTagsField(forms.ModelMultipleChoiceField):
    widget = UserTagsWidget
    def clean(self, value):
        print 'TODO: core.models.UserTagsField move to widget file'
        value = super(UserTagsField, self).clean(value)
        #P '------vlue:', value
        
        return value
        
