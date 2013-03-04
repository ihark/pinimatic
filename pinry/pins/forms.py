from django import forms

from taggit.forms import TagField, TagWidget
from pinry.core.forms import CustomTagField, UserTagsField
print '-import pinry.core.forms'
from .models import Pin
from pinry.core.widgets import CustomImage, CustomThumbnail, AdminImageWidget
from django.forms.widgets import FileInput, HiddenInput, TextInput
from pinry.settings import IMAGES_PATH, MEDIA_URL
import re
#from pinry.core.utils import MakeThumbnail, saveTempImg
from pinry.core.utils import format_tags, format_tags_list


class PinForm(forms.ModelForm):
    
    id = forms.CharField(widget=HiddenInput(attrs={'style':'display: none;'}), label='id', required=False)
    srcUrl = forms.CharField(widget=HiddenInput(attrs={'style':'display: none;'}), label='srcUrl', required=False)
    imgUrl = forms.CharField(widget=TextInput(attrs={'placeholder':'http://www.xxx.com/image.ext'}), label='Image URL', required=False)
    #thumbnail = forms.ImageField(widget=CustomThumbnail(), label='Current', required=False)
    image = forms.ImageField(widget=FileInput(),label='or Upload', required=False)
    uImage = forms.CharField(widget=HiddenInput(attrs={'style':'display: none;'}), required=False)
    repin = forms.CharField(widget=HiddenInput(attrs={'style':'display: none;'}),required=False, initial=None)
    tags = CustomTagField(label='*New Tag ?', help_text='You can enter multiple tags seperated by spaces, commas, or quotes: '
                                                      'tagone  tagtwo =(Tagone) (Tagtwo) / '
                                                      'tag one,  tag two = (Tag one) (Tag two) / '
                                                      'one  two  "tag, three" = (One) (Two) (tag, three)', 
                                                      required=False)
    tagsUser = UserTagsField(queryset=Pin.tags.all(), help_text='Use CONTROLL + CLICK to add or remove tags', label='*Your Tags ?', required=False)
    #tagsTest = ComboField(queryset=Pin.tags.all(), label='*Your Tags', required=False)

    #NOTE: passing in user breaks tags validation, why?????
    def __init__(self, *args, **kwargs):
        print '--form init'
        user = kwargs.pop('user', None)
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        print '--form super ini'
        if user:
            qs = Pin.tags.most_common().filter(pin__submitter__exact=user).order_by('name')#num_times
            self.fields['tagsUser'].queryset = qs #TODO: need to convert to set in UserTagsWidget
            self.fields['tagsUser'].initial = Pin.tags.all().filter(pin__exact=self.instance)
            tags_initial = self.fields['tagsUser'].initial
        
        self.fields.keyOrder = (
            'id',
            'srcUrl',
            'imgUrl',
            #'thumbnail',
            'image',
            'description',
            'uImage',
            'repin',
            'tagsUser',
            'tags',
        )

        print "--form end init"

    def check_if_image(self, data):
        print '--form check_if_img()'
        image_file_types = ['png', 'gif', 'jpeg', 'jpg', 'none']
        file_url = data.split('?')[0]
        print 'file type: '+file_url
        p = file_url.rfind('.')
        s = file_url.rfind('/')
        print 'p: '+str(p)
        print 's: '+str(s)
        if p != -1 and p > s:
            file_type = file_url.split('.')[-1]
        else:
            file_type = 'none'
        print 'file type: '+file_type
        if file_type.lower() not in image_file_types:
            raise forms.ValidationError("Requested URL is not an image file. "
                                        "Only images are currently supported.")
    def clean_repin(self):
        print '--form clean_repin'
        data = self.cleaned_data['repin']
        if data == '':
            data = None
        else:
            data = Pin.objects.get(id = data)
        return data

    def clean_tags(self):
        print '--form clean_tags'
        tags_new = self.cleaned_data['tags']
        for tag in tags_new:
            print 'tag in: ', tag
            url = re.match(r'http://|https://', tag)
            print url
            if url: raise forms.ValidationError("Form: Tags can not be url's")
            length = len(tag)
            if length>10: raise forms.ValidationError("Form: Max tag length is 10 charicters")
            
        tags_new = format_tags_list(tags_new) #new formatted tags to be assigned to pin
        try:#find tag names in list of all user tags
            tags_all_data = self['tagsUser']
            tags_all_list = re.findall(r'<.*?>(.+?)<.*?>', str(tags_all_data))
        except:
            tags_all_list = None
        try:#find currently selected tag names in list of all user tags
            print 'self.cleaned_data["tagsUser"]: ', self.cleaned_data['tagsUser']
            tags_keep = [str(item) for item in self.cleaned_data['tagsUser'].values_list('name', flat=True)]
            print 'tags_keep: ', tags_keep
        except:
            tags_keep = None
        try:#find original selected tag names in list of all user tags
            tags_orig = [str(item) for item in self.instance.tags.all().values_list('name', flat=True)]
        except:
            tags_orig = None
        if tags_keep and tags_orig: 
            #TODO: delete these tags if not used by other users.
            tags_diff = [item for item in tags_orig if not item in tags_keep]
        if tags_keep:    
            data = tags_keep + tags_new
        else:
            data = tags_new
        '''DEBUG
        print '-tags psot format:', tags_new 
        print '-tags_all_list:', tags_all_list
        print '-tags_keep:', tags_keep 
        print '-tags_orig:', tags_orig 
        print '-tags_diff:', tags_diff 
        print 'returned data:', data
        '''
        #Make sure there is at least one tag
        if len(data)>0:
            return data
        else:
            raise forms.ValidationError("Form: You must provide at least one tag.  Select from list above or enter new comma seperated tags below.")

    def clean(self):
        print '--form clean'
        cleaned_data = super(PinForm, self).clean()
        id = cleaned_data.get('id')
        imgUrl = cleaned_data.get('imgUrl')
        image = cleaned_data.get('image')
        uImage = cleaned_data.get('uImage')
        repin = cleaned_data.get('repin')
        #tags = cleaned_data.get('tags')
        #tagsUser = cleaned_data.get('tagsUser')
        #create saved_data attribute accecable by view with bound form
        self.saved_data = cleaned_data
        
        if image and imgUrl and not id:
            print '--form image and imgUrl and not id'
            raise forms.ValidationError("Choose a url OR upload")
        print 'repin = ', repin  
        if imgUrl and not id and not repin:
            print '--form imgUrl without ID found: '+str(imgUrl)
            self.check_if_image(imgUrl)
            try:
                Pin.objects.get(imgUrl=imgUrl)
                raise forms.ValidationError("URL has already been pinned!")
            except Pin.DoesNotExist:
                protocol = imgUrl.split(':')[0]
                if protocol == 'http':
                    opp_url = imgUrl.replace('http://', 'https://')
                elif protocol == 'https':
                    opp_url = imgUrl.replace('https://', 'http://')
                else:
                    raise forms.ValidationError("Currently only support HTTP and "
                                                "HTTPS protocols, please be sure "
                                                "you include this in the URL.")

                try:
                    Pin.objects.get(imgUrl=opp_url)
                    raise forms.ValidationError("URL has already been pinned!")
                except Pin.DoesNotExist:
                    pass
        elif imgUrl:
            print '--form  imgUrl with ID found: '+str(imgUrl)
        elif image:
            print '--form  image found ID or NO ID: '+str(image)
        elif uImage:
            print '*****************uimage detected'+uImage
       
        else:
            raise forms.ValidationError("Need either a url OR upload.")

        #update saved_data
        self.saved_data=self.cleaned_data
        return cleaned_data

    class Meta:
        model = Pin
        exclude = ['submitter', 'thumbnail', 'tagsUser']
