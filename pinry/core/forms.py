from taggit.forms import TagField, TagWidget
from django.forms.widgets import SelectMultiple
from django import forms
from django.utils.translation import ugettext as _
from taggit.utils import parse_tags, edit_string_for_tags
import re

from pinry.core.utils import format_tags


class CustomTagWidget(forms.TextInput):
    def render(self, name, value, attrs=None):
        attrs={'placeholder':'add new tags here'}
        print '----CustomTagWidjget render exicuted'
        #print "widget attrs", attrs
        #print "widget value",value
        #print "widget name",name
        if value is not None and not isinstance(value, basestring):
            value = edit_string_for_tags([o.tag for o in value.select_related("tag")])
            #remove all quotes from tag values when rendered on form
            #value = re.sub(r'"', '', value)
            value = ""#remove exising values from form
        return super(CustomTagWidget, self).render(name, value, attrs)


class CustomTagField(forms.CharField):
    widget = CustomTagWidget

    def clean(self, value):
        value = super(CustomTagField, self).clean(value)
        print '----CustomTagField form clean exicuted'
        print "customTagFiled Clean value",value
        if value:
            try:
                value = format_tags(value)
                return parse_tags(value)
            except ValueError:
                print '****CustomTagField ValueError'
                raise forms.ValidationError("Provide one or more comma-separated tags.")
        else: 
            return []
                
class UserTagsWidget(forms.SelectMultiple):
    def render(self, name, value, attrs=None):
        #print '----UserTagsWidget render exicuted'
        #self.choices = set(self.choices)
        #print self.choices
        #for c in self.choices: print 'choices:', c
        
        return super(UserTagsWidget, self).render(name, value, attrs)
                
class UserTagsField(forms.ModelMultipleChoiceField):
    widget = UserTagsWidget
    def clean(self, value):
        value = super(UserTagsField, self).clean(value)
        #print '----UserTagsField form clean exicuted'
        #print '------vlue:', value
        
        return value
        
