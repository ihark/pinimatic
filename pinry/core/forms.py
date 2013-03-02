from taggit.forms import TagField, TagWidget
from django.forms.widgets import SelectMultiple
from django import forms
from django.utils.translation import ugettext as _
from taggit.utils import parse_tags, edit_string_for_tags
import re


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
            value = ""
        return super(CustomTagWidget, self).render(name, value, attrs)


class CustomTagField(forms.CharField):
    widget = CustomTagWidget

    def clean(self, value):
        value = super(CustomTagField, self).clean(value)
        print '----CustomTagField form clean exicuted'
        print "customTagFiled Clean value",value
        if value:
            try:
                #check for comma-sep list
                comma = re.match(r'.*?,', value)
                #remove any spaces between quote and first charicter
                value = re.sub(r'"\s+?(?P<tag>[^\s].*?")', '"'+r'\g<tag>', value)
                #find quoted tags & make list
                quotedTags = re.findall(r'".*?"', value)
                #remove quoted from value string and make list
                for qt in quotedTags:
                    value = value.replace(qt,'')
                uQuotedTags = value.split(',')
                #strip white space from uQuoted
                uQuotedTags = [tag.strip() for tag in uQuotedTags]
                #remove blank tags
                uQuotedTags = filter(bool, uQuotedTags)
                print '*uQuotedTags: ', uQuotedTags
                #handle coma-sep list of tags (first letter of each tag to uppercase)
                if comma:
                    value = ', '.join(tag[0].upper() + tag[1:].lower() for tag in uQuotedTags)
                #handle space-sep list of tags (first letter of each tag uppercase)
                elif uQuotedTags:
                    value = ' '.join(word[0].upper() + word[1:].lower() for word in uQuotedTags[0].split(' '))
                #handle quoted tags (no change)
                if quotedTags:
                    value += ' '
                    value += ' '.join(tag[0] + tag[1:] for tag in quotedTags)
                print 'parse', parse_tags(value)
                return parse_tags(value)

            except ValueError:
                print '****CustomTagField ValueError'
                raise forms.ValidationError(_("Provide one or more comma-separated tags."))
          
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
        
