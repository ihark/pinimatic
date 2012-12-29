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
#from pinry.settings import MEDIA_URL, IMAGES_PATH, SITE_URL
import os
from django.core.files.storage import default_storage
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
      
    # save the file
    hash_name = os.urandom(32).encode('hex')
    tmpName = hash_name+filename
    tmpPath = settings.TMP_ROOT
    tmpUrl = settings.SITE_URL+settings.TMP_URL+tmpName
    savePath = tmpPath+tmpName 
    success = save_upload( upload, savePath, is_raw )
    print success
    # let Ajax Upload know whether we saved it or not
    ret_json = { 'success': success, 'tmpName':tmpName, 'tmpUrl':tmpUrl, }
    return HttpResponse( json.dumps( ret_json ) )

#save uploaded image    
def save_upload( uploaded, filePath, raw_data ):
  
  tmpPath = settings.TMP_ROOT
  print 'save_uplaod filename: '+filePath
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
    exists = default_storage.exists(settings.TMP_ROOT+fileName)
    success = 'utils - File has been found'
    print success
    if exists:
        default_storage.delete(settings.TMP_ROOT+fileName)
        success = 'utils - File has been deleted'
    else:
        success = 'utils - File was not found'
    if request:
        success = 'utils - File was deleted (json sent)'
        ret_json = { 'success': success, }
        return HttpResponse( json.dumps( ret_json ) )
    print success
  
