from django.db import models
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.contrib.auth.models import User

from taggit.managers import TaggableManager
import urllib2
import os
from PIL import Image
from pinry.settings import MEDIA_URL, IMAGES_PATH, SITE_URL, TMP_ROOT
#from django.conf import settings
from django.core.files.storage import default_storage
from pinry.core.utils import delete_upload


class Pin(models.Model):
    submitter = models.ForeignKey(User)
    imgUrl = models.TextField(blank=True, null=True)
    srcUrl = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=IMAGES_PATH)
    thumbnail = models.ImageField(upload_to='pins/pin/thumbnails/', max_length=100)
    published = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()


    def __unicode__(self):
        return self.imgUrl

    def edit(self, *args, **kwargs):
        print 'model - pin.edit()'
        exPin = Pin.objects.get(pk=self.pk)
        if self.uImage:
            print 'model - new image detected'
            self.image.delete()
            self.thumbnail.delete()
            default_storage.delete(exPin.image.path)
            default_storage.delete(exPin.thumbnail.path)
            self.imgUrl = 'Uploaded'
            self.srcUrl = None
        elif not self.imgUrl:
            self.imgUrl = exPin.imgUrl
        if exPin.imgUrl != self.imgUrl and self.imgUrl != 'Uploaded':
            print 'model - new URL detected'
            self.image.delete()
            self.thumbnail.delete()
            default_storage.delete(exPin.image.path)
            default_storage.delete(exPin.thumbnail.path)
            self.srcUrl = self.imgUrl


    def save(self, *args, **kwargs):
        hash_name = os.urandom(32).encode('hex')
        if not self.image:
            print 'model - if not self.image'
            temp_img = NamedTemporaryFile()
            if self.uImage:
                print 'model - self.uImage'
                image = Image.open(TMP_ROOT+self.uImage)
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
            if self.uImage:
                delete_upload(None, self.uImage)
                #default_storage.delete(TMP_ROOT+self.uImage)

        if not self.thumbnail:
            print 'model - if not self.thumbnail'
            if not self.image:
                image = Image.open(temp_img.name)
            else:
                super(Pin, self).save()
                image = Image.open(self.image.path)
            size = image.size
            prop = 200.0 / float(image.size[0])
            size = (int(prop*float(image.size[0])), int(prop*float(image.size[1])))
            image.thumbnail(size, Image.ANTIALIAS)
            temp_thumb = NamedTemporaryFile()
            if image.mode != "RGB":
                image = image.convert("RGB")
            image.save(temp_thumb.name, 'JPEG')
            self.thumbnail.save(''.join([hash_name, '.jpg']), File(temp_thumb))
            print 'model - thumbnail complete'
        
        if not self.imgUrl:
            self.imgUrl = 'Uploaded' #SITE_URL+MEDIA_URL+IMAGES_PATH+self.image.name
        if not self.srcUrl:
            print self.image.name
            print self.image.path
            self.srcUrl = MEDIA_URL+self.image.name

        super(Pin, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-id']
