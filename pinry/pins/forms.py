from django import forms

from taggit.forms import TagField

from .models import Pin
from pinry.core.widgets import CustomImage, CustomThumbnail
from django.forms.widgets import HiddenInput


class PinForm(forms.ModelForm):
    id = forms.CharField(widget=HiddenInput(attrs={'style':'display: none;'}), label='id', required=False)
    imgUrl = forms.CharField(label='Image URL', required=False)
    #thumbnail = forms.ImageField(widget=CustomThumbnail(), label='Current', required=False)
    image = forms.ImageField(widget=CustomImage(),label='or Upload', required=False)
    tags = TagField()


    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = (
            'id',
            'imgUrl',
            #'thumbnail',
            'image',
            'description',
            'tags',
        )


    def check_if_image(self, data):
        # Test file type
        image_file_types = ['png', 'gif', 'jpeg', 'jpg']
        file_type = data.split('.')[-1]
        if file_type.lower() not in image_file_types:
            raise forms.ValidationError("Requested URL is not an image file. "
                                        "Only images are currently supported.")

    def clean(self):
        cleaned_data = super(PinForm, self).clean()
        id = cleaned_data.get('id')
        imgUrl = cleaned_data.get('imgUrl')
        image = cleaned_data.get('image')
        
        if id:
            pass
            print 'validate id: '+str(id)
        elif imgUrl:
            #print '--checking url for exiting, edit = '+edit
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
        elif image:
            pass
        else:
            raise forms.ValidationError("Need either a URL or Upload.")

        return cleaned_data

    class Meta:
        model = Pin
        exclude = ['submitter', 'thumbnail']
