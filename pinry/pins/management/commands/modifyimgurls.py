#http://pinimatic.s3.amazonaws.com
#http://192.168.1.100:5000

from django.core.management.base import BaseCommand, CommandError
from pinry.pins.models import Pin
import re

class Command(BaseCommand):
    args = '<new_domain>'
    help = 'modify the image url domain for all pins, enter new doamin: \
            modifyimgurls <xxx.xxx.xxx>'
  
    def handle(self, *args, **options):
        try:
            new_domain = args[0]
        except:
            raise CommandError('You must specify a domain: modifyimgurls <xxx://xxx.xxx.xxx>')
        found = re.findall('\w*?://[^/]*?', str(new_domain))
        if found:
            pins = Pin.objects.all()
            for pin in pins:
                new_img_url = re.sub('\w*?://.*?/', new_domain+'/', pin.image.url)
                is_domain = re.findall('\w*?://.*?/', new_img_url)
                if not is_domain:
                    new_img_url = re.sub('/', new_domain+'/', pin.image.url)
                pin.imgUrl = new_img_url
                #print('new_img_url:', pin.imgUrl)
                super(Pin, pin).save()
                self.stdout.write('-Successfully updated url to: "%s"' % pin.imgUrl)
        else:
            raise CommandError('You must specify domain: modifyimgurls <xxx://xxx.xxx.xxx>')
        
        
        
        
        
