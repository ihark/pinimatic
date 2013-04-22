from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from PIL import Image
import StringIO
import json
import tempfile
from django.utils import simplejson
from django.http import HttpResponse, Http404
from django.conf import settings
import os
import re
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core.files.images import ImageFile

#ajax thumbnail uplaod
#get uploaded image and pass to save    
def ajax_upload( request ):
  if request.method == "POST":
    if request.is_ajax( ):
      # the file is stored raw in the request
      upload = request
      is_raw = True
      # AJAX Upload will pass the filename in the querystring if it is the "advanced" ajax upload
      try:
        filename = request.GET[ 'qqfile' ]
        print 'ajax_uplaod filename: '+filename
      except KeyError: 
        return HttpResponseBadRequest( "AJAX request not valid" )
    # not an ajax upload, so it was the "basic" iframe version with submission via form
    else:
      is_raw = False
      if len( request.FILES ) == 1:
        # FILES is a dictionary in Django but Ajax Upload gives the uploaded file an
        # ID based on a random number, so it cannot be guessed here in the code.
        # Rather than editing Ajax Upload to pass the ID in the querystring,
        # observer that each upload is a separate request,
        # so FILES should only have one entry.
        # Thus, we can just grab the first (and only) value in the dict.
        upload = request.FILES.values( )[ 0 ]
      else:
        raise Http404( "Bad Upload" )
      filename = upload.name
      
    #removed for file name preservation: hash_name = os.urandom(32).encode('hex')
    tmpName = request.user.username+filename
    tmpPath = settings.TMP_ROOT
    tmpUrl = settings.TMP_URL+tmpName
    savePath = tmpPath+tmpName
    print 'ajax_uplaod savePath: '+savePath
    success = save_upload( upload, savePath, is_raw )
    print success
    # let Ajax Upload know whether we saved it or not
    ret_json = { 'success': success, 'tmpName':tmpName, 'tmpUrl':tmpUrl, }
    return HttpResponse( json.dumps( ret_json ) )

#save uploaded image    
def save_upload( uploaded, filePath, raw_data ):
  
  tmpPath = settings.TMP_ROOT
  'save_uplaod tmpPath: '+tmpPath
  #if not os.path.isdir(tmpPath):
  print '------creating dir @ tempPath:'
  print tmpPath
  e = os.path.isdir(tmpPath)
  print e
  if not e:
      os.makedirs(tmpPath)
      e = os.path.isdir(tmpPath)
      print e
  
  print 'save_uplaod filepath: '+filePath
  ''' 
  raw_data: if True, uploaded is an HttpRequest object with the file being
            the raw post data 
            if False, uploaded has been submitted via the basic form
            submission and is a regular Django UploadedFile in request.FILES
  '''
  try:
    from io import FileIO, BufferedWriter
    with BufferedWriter( FileIO( filePath, "wb" ) ) as dest:
      print dest
      # if the "advanced" upload, read directly from the HTTP request 
      # with the Django 1.3 functionality
      if raw_data:
        foo = uploaded.read( 1024 )
        while foo:
          dest.write( foo )
          foo = uploaded.read( 1024 ) 
      # if not raw, it was a form upload so read in the normal Django chunks fashion
      else:
        for c in uploaded.chunks( ):
          dest.write( c )
      # got through saving the upload, report success
      return True
  except IOError:
    print 'could not open the file most likely'
    pass
  return False
  
#deletes uploaded image

def delete_upload(request, fileName = None):
    print 'utils delete_uplaod called: '+fileName
    tempFS = FileSystemStorage(location=settings.TMP_ROOT)
    try:
        tempFS.delete(settings.TMP_ROOT+fileName)
        success = 'utils - File has been deleted'
    except:
        success = 'utils - File was not found'
    if request:
        success = 'utils - File was deleted (json sent)'
        ret_json = { 'success': success, }
        return HttpResponse( json.dumps( ret_json ) )
    print success

#apply formating to tags string
#TODO: this is retarded, could have used parse_tags(value) to get tags array then did my formats....
def format_tags(value):
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
        return value
    except ValueError:
        print '****CustomTagField ValueError'
        return False
        
def format_tags_list(value):
    try:
        #first letter of each tag to uppercase
        value = [tag[0].upper() + tag[1:].lower() for tag in value]
        return value
    except ValueError:
        print '****CustomTagField ValueError'
        return False
