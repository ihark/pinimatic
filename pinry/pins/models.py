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
from django.contrib.comments.models import Comment
from django.contrib.contenttypes import generic

from follow import utils

class Pin(models.Model):
    submitter = models.ForeignKey(User)
    imgName = models.TextField(blank=True, null=True)
    imgUrl = models.TextField(blank=True, null=True)
    srcUrl = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to=settings.IMAGES_PATH)
    thumbnail = models.ImageField(upload_to='pins/pin/thumbnails/', max_length=100)
    published = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()
    repin = models.ForeignKey('self', blank=True, null=True, on_delete=models.SET_NULL)
    comments = generic.GenericRelation(Comment,
                               content_type_field='content_type',
                               object_id_field='object_pk')


    def __unicode__(self):
        if self.imgName:
            return self.imgName
        else:
            return self.imgUrl
        
    def admin_thumb(self):
        return '<img height="50px" src="%s"/>' % self.thumbnail.url
    admin_thumb.allow_tags = True
    
    def edit(self, *args, **kwargs):
        print 'model - pin.edit()'
        exPin = Pin.objects.get(pk=self.pk)
        if self.uImage:
            print 'model - new image detected'
            self.image = None
            self.thumbnail = None
            default_storage.delete(exPin.image.url)
            default_storage.delete(exPin.thumbnail.url)
            self.imgUrl = None
            self.srcUrl = None
        elif not self.imgUrl:
            self.imgUrl = exPin.imgUrl
        if exPin.imgUrl != self.imgUrl and self.imgUrl:
            print 'model - new URL detected'
            self.image = None
            self.thumbnail = None
            print 'exPin.image.path: ', exPin.image
            default_storage.delete(exPin.image.name)
            default_storage.delete(exPin.thumbnail.name)
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
                self.imgName = self.uImage
            if self.imgUrl:
                print 'model - self.image'
                temp_img.write(urllib2.urlopen(self.imgUrl).read())
                temp_img.flush()
                image = Image.open(temp_img.name)
                self.imgName = self.imgUrl
            if image.mode != "RGB":
                print 'model - image.mode'
                image = image.convert("RGB")
            image.save(temp_img.name, 'JPEG')
            self.image.save(''.join([hash_name, '.jpg']), File(temp_img))
            #create image thumbnail
            print 'model - starting thumbnail'
            temp_thumb = NamedTemporaryFile()
            size = image.size
            prop = 200.0 / float(image.size[0])
            size = (int(prop*float(image.size[0])), int(prop*float(image.size[1])))
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(temp_thumb.name, 'JPEG')
            self.thumbnail.save(''.join([hash_name, '.jpg']), File(temp_thumb))
            #super(Pin, self).save()
            if self.uImage:
                print 'model - delete_uplaod called'
                delete_upload(None, self.uImage)
        media_url = settings.MEDIA_URL
        if not self.srcUrl:
            print 'model - if not srcUrl'
            self.srcUrl = media_url+self.image.name
        #always link to our saved image to prevent linking back to dead images.
        self.imgUrl = media_url+self.image.name
        super(Pin, self).save(*args, **kwargs)
    
    class Meta:
        ordering = ['-id']

utils.register(Pin, 'favorite', 'f_pin')
utils.register(User, 'folowing', 'f_user')