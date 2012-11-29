from django import forms

from taggit.forms import TagField, TagWidget

from .models import Pin
from pinry.core.widgets import CustomImage, CustomThumbnail, AdminImageWidget
from django.forms.widgets import FileInput, HiddenInput
from pinry.settings import IMAGES_PATH, MEDIA_URL
#from pinry.core.utils import MakeThumbnail, saveTempImg


class PinForm(forms.ModelForm):
    id = forms.CharField(widget=HiddenInput(attrs={'style':'display: none;'}), label='id', required=False)
    srcUrl = forms.CharField(widget=HiddenInput(attrs={'style':'display: none;'}), label='srcUrl', required=False)
    imgUrl = forms.CharField(label='Image URL', required=False)
    #thumbnail = forms.ImageField(widget=CustomThumbnail(), label='Current', required=False)
    image = forms.ImageField(widget=FileInput(),label='or Upload', required=False)
    tags = TagField(widget=TagWidget(attrs={'placeholder':'required'}), label='*Tags')
    uImage = forms.CharField(widget=HiddenInput(attrs={'style':'display: none;'}), required=False)


    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = (
            'id',
            'srcUrl',
            'imgUrl',
            #'thumbnail',
            'image',
            'description',
            'tags',
            'uImage',
        )


    def check_if_image(self, data):
        print '--form check_if_img()'
        # Test file type
        image_file_types = ['png', 'gif', 'jpeg', 'jpg']
        file_type = data.split('.')[-1]
        file_type = file_type.split('?')[0]
        if file_type.lower() not in image_file_types:
            raise forms.ValidationError("Requested URL is not an image file. "
                                        "Only images are currently supported.")

    def clean(self):
        cleaned_data = super(PinForm, self).clean()
        id = cleaned_data.get('id')
        imgUrl = cleaned_data.get('imgUrl')
        image = cleaned_data.get('image')
        uImage = cleaned_data.get('uImage')
        #create saved_data attribute accecable by view with bound form
        self.saved_data = cleaned_data
        
        if image and imgUrl and not id:
            print '--form image and imgUrl and not id'
            raise forms.ValidationError("Choose a url OR upload")
            
        if imgUrl and not id:
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
        exclude = ['submitter', 'thumbnail']
