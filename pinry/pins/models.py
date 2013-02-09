from django.db import models
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.contrib.auth.models import User

from taggit.managers import TaggableManager
import urllib2
import os
from PIL import Image
from django.conf import settings
from django.core.files.storage import default_storage
from pinry.core.utils import delete_upload

from follow import utils



class Pin(models.Model):
    submitter = models.ForeignKey(User)
    imgUrl = models.TextField(blank=True, null=True)
    srcUrl = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=settings.IMAGES_PATH)
    thumbnail = models.ImageField(upload_to='pins/pin/thumbnails/', max_length=100)
    published = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()
    repin = models.ForeignKey('self', blank=True, null=True)


    def __unicode__(self):
        return self.imgUrl

    def edit(self, *args, **kwargs):
        print 'model - pin.edit()'
        exPin = Pin.objects.get(pk=self.pk)
        if self.uImage:
            print 'model - new image detected'
            self.image.delete()
            self.thumbnail.delete()
            default_storage.delete(exPin.image.url)
            default_storage.delete(exPin.thumbnail.url)
            self.imgUrl = 'Uploaded'
            self.srcUrl = None
        elif not self.imgUrl:
            self.imgUrl = exPin.imgUrl
        if exPin.imgUrl != self.imgUrl and self.imgUrl != 'Uploaded':
            print 'model - new URL detected'
            self.image.delete()
            self.thumbnail.delete()
            default_storage.delete(exPin.image.url)
            default_storage.delete(exPin.thumbnail.url)
            self.srcUrl = self.imgUrl


    def save(self, *args, **kwargs):
        hash_name = os.urandom(32).encode('hex')
        #create image
        if not self.image:
            print 'model - if not self.image'
            temp_img = NamedTemporaryFile()
            if self.uImage:
                print 'model - self.uImage'
                image = Image.open(settings.TMP_ROOT+self.uImage)
            if self.imgUrl:
                print 'model - self.image'
                temp_img.write(urllib2.urlopen(self.imgUrl).read())
                temp_img.flush()
                image = Image.open(temp_img.name)
            if image.mode != "RGB":
                print 'model - image.mode'
                image = image.convert("RGB")
            image.save(temp_img.name, 'JPEG')
            self.image.save(''.join([hash_name, '.jpg']), File(temp_img))
            #create image thumbnail
            print 'model - starting thumbnail'
            super(Pin, self).save()
            temp_thumb = NamedTemporaryFile()
            size = image.size
            prop = 200.0 / float(image.size[0])
            size = (int(prop*float(image.size[0])), int(prop*float(image.size[1])))
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(temp_thumb.name, 'JPEG')
            self.thumbnail.save(''.join([hash_name, '.jpg']), File(temp_thumb))
            print 'model - delete_uplaod called'
            if self.uImage:
                delete_upload(None, self.uImage)
            print 'model - thumbnail complete'
        
        if not self.srcUrl:
            print 'if not srcUrl'
            print self.image.name
            print self.image.url
            print self.srcUrl
            if self.imgUrl:
                self.srcUrl = self.imgUrl
            else:
                self.srcUrl = settings.MEDIA_URL+self.image.name

        if not self.imgUrl:
            self.imgUrl = 'Uploaded'
            
        super(Pin, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ['-id']

utils.register(Pin, 'favorite', 'f_pin')
utils.register(User, 'folowing', 'f_user')