/**
 * Based on Wookmark's endless scroll.
 */
var apiURL = '/api/v1/pin/?format=json&offset='
var page = 0;
var handler = null;
var globalTag = null;
var isLoading = false;

/**
 * When scrolled all the way to the bottom, add more tiles.
 */
function onScroll(event) {
  if(!isLoading) {
      var closeToBottom = ($(window).scrollTop() + $(window).height() > $(document).height() - 100);
      if(closeToBottom) loadData();
  }
};

function applyLayout() {
  $('#pins').imagesLoaded(function() {
      // Clear our previous layout handler.
      if(handler) handler.wookmarkClear();
      
      // Create a new layout handler.
      handler = $('#pins .pin');
      handler.wookmark({
          autoResize: true,
          offset: 3,
          itemWidth: 242
      });
  });
};

/**
 * Loads data from the API. 
 *(tag set by tag click user set by nav bar button)
 */
//?*Need method for detecting back button or watch url(0) for changes.
function loadData(tag, user) {
    isLoading = true;
    $('#loader').show();
	
	console.warn('first user: '+user)
	console.warn('first Tag: '+tag)

	//check url for current user / tag
	if (url(2) && url(2) != 'all') {
		console.warn('url(2)sets user to: '+url(2))
		cUser = url(2)
    }else if (!user){ //if no current user and no new user set to 'all'
		user = 'all'
		cUser = user
	}
	if (url(3) && tag !== null) {
		console.warn('url(3) sets tag to : '+url(3))
		tag = url(3)
    }
	//if new user or new tag selected
	if (user && !tag) {
		var nAddress = '/pins/'+user+'/'
		console.warn('if user update url to: /pins/'+user+'/')
        window.history.pushState(user, 'Pinry - User - '+user, nAddress);

	} else if (tag && !user) {
		var nAddress = '/pins/'+cUser+'/'+tag+'/'
		console.warn('else if tag update url to: '+nAddress)
        window.history.pushState(tag, 'Pinry - Tag - '+tag, nAddress);
	}else if (tag && user){
		var nAddress = '/pins/'+user+'/'+tag+'/'
		console.warn('else if tag update url to: '+nAddress)
        window.history.pushState(tag, 'Pinry - Tag - '+tag, nAddress);
	}
	
	if (tag !== undefined || user !== undefined && user !== cUser){
		page = 0;
		$('#pins').html('');

	}
    if (tag !== undefined) {
        //$('#pins').html('');
        if (tag != null)
            $('.tags').html('<span class="label tag" onclick="loadData(null)">' + tag + ' x</span>');
        else {
            $('.tags').html('');
            window.history.pushState(tag, 'Pinry - Recent Pins', '/pins/'+cUser+'/');
        }
    }
	console.warn('page: '+page)
    var loadURL = apiURL+(page*30);
	console.warn('final user: '+user)
	console.warn('final tag: '+tag)
	if (user && user != 'all') loadURL += "&user=" + user;
    if (tag && tag !== null) loadURL += "&tag=" + tag;
    $.ajax({
        url: loadURL,
		contentType: 'application/json',
		beforeSend: function(jqXHR, settings) {
			jqXHR.setRequestHeader('X-CSRFToken', $('input[name=csrfmiddlewaretoken]').val());
		},
        success: onLoadData,
		error: function(jqXHR, settings) {
			alert(error);
		},
    });
};

/**
 * Receives data from the API, creates HTML for images and updates the layout
 */
function onLoadData(data) {
    data = data.objects;
    isLoading = false;
    $('#loader').hide();
    
    page++;
    
    var html = '';
    var i=0, length=data.length, image;
    for(; i<length; i++) {
      image = data[i];
      html += '<div class="pin">';
          html += '<div class="pin-options">';
              html += '<a href="/pins/delete-pin/'+image.id+'">';
                  html += '<i class="icon-trash"></i>';
              html += '</a>';
			  html += '<a href="/pins/edit-pin/'+image.id+'">';
                  html += '<i class="icon-edit"></i>';
              html += '</a>';
          html += '</div>';
          html += '<a class="fancybox" rel="pins" href="'+image.image+'">';
              html += '<img src="'+image.thumbnail+'" width="200" >';
          html += '<a class="source-url" rel="pins" href="'+image.srcUrl+'">';
		      html += '<span>Visit Origninal Website</span>';
		  html += '</a>';
          if (image.description) html += '<p>'+image.description+'</p>';
          if (image.tags) {
              html += '<p>';
              for (tag in image.tags) {
                  html += '<span class="label tag" onclick="loadData(\'' + image.tags[tag] + '\')">' + image.tags[tag] + '</span> ';
              }
              html += '</p>';
          }
      html += '</div>';
    }
    
    $('#pins').append(html);
    
    applyLayout();
};

$(document).ready(new function() {
    $(document).bind('scroll', onScroll);
    loadData();
});

/**
 * On clicking an image show fancybox original.
 */
$('.fancybox').fancybox({
    openEffect: 'none',
    closeEffect: 'none'
});

/**
 * Edit pin functions.
 */

$(document).ready(function() {
	//global vars
	prevUpload = false;
	thumbTarget = 'img#thumb_id'
	cUrl = $(thumbTarget).attr("src")
	console.warn('document ready,  thumbTarget: '+thumbTarget+' / cUrl: '+cUrl)
	fileUploaders = replaceFileUpload('div#div_id_image');//*set fileFiled to disapy none on html then set to block after load
	console.warn('fileUploaders = ')
	console.warn(fileUploaders)
	//addClearToFileUploadBtn('.qq-upload-button');
	onFileChange();
	onUrlChange();
});
//detect file changes
function onFileChange(thumb) {
	$('imput#id_uImage').change(function() {
		console.warn('image changed - updating thumb');
		updateThumb(thumbTarget, this, 'input#id_imgUrl');
	});
}
//detect url changes
function onUrlChange() {
	$('input#id_imgUrl').change(function() {
		console.warn('url change detected');
		updateThumb(thumbTarget, this);
	});
}


//Replaced the specified target with the file-uploader element, Requires file-uplader.js
//an element targeted by id(#) must be prefixed by an element

function replaceFileUpload(target){
	var i = 0
	var fileUploaders = []
	$(target).each(function() {
		var fileUploader = new qq.FileUploader( {
			action: "/ajax/thumb/",
			element: $(target)[i],
			multiple: false,
			allowedExtensions: ['jpg', 'jpeg', 'png', 'gif'],               
			sizeLimit: 0,   
			minSizeLimit: 0,
			template: '<div class="qq-uploader">' + 
                '<div class="qq-upload-drop-area"><span>Drop files here to upload</span></div>' +
                '<div class="qq-upload-button">Click to Browse or Drag Image Here</div>' +
                '<ul class="qq-upload-list"></ul>' + 
             '</div>',
			onError: function(id, fileName){
				//get error image
				$(thumbTarget).attr("src", '');
			},
			onSubmit: function(id, fileName){
				//remove previous item from list
				$('.qq-upload-list').children().remove()
				//get loading image
				$(thumbTarget).attr("src", '/static/core/img/thumb-loader.gif');
			},
			onComplete: function( id, fileName, responseJSON ) {
				if( responseJSON.success ) {
					console.warn('image uplaod success!');
					onFileChange();
					//store and delete previoius thumb
					prevUpload = $('input#id_uImage').val();
					console.warn('prevUpload = '+prevUpload);
					if (prevUpload){
						uImageDelete(prevUpload);
					}
					//update uImage with tmpName for form and model
					$('input#id_uImage').attr("value", responseJSON.tmpName);
					//update variable with current uploaded file name for deletion
					uFileName = responseJSON.tmpName
					//update thumb
					updateThumb(thumbTarget, responseJSON, '#id_imgUrl');

				}else{
					console.warn('image uplaod failed :(')
				}
			},
			onAllComplete: function( uploads ) {
				// uploads is an array of maps
				// the maps look like this: { file: FileObject, response: JSONServerResponse }
				console.warn('All uploads complete!: '+uploads)
				//re attach onFileChange due to html reset in file uplaoder
			},
			params: {
			  'csrf_token': '{{ csrf_token }}',
			  'csrf_name': 'csrfmiddlewaretoken',
			  'csrf_xname': 'X-CSRFToken',
			},
		} ) ;
		//modify file uploader properties
		fileUploader._formatFileName = function(name){
			if (name.length > 15){
				name = name.slice(0, 15) + '...' + name.slice(-4);    
			}
			return name;
		}
		fileUploaders[i] = fileUploader;
		i++;
	});
	return fileUploaders
}

//(currently not used) wraps fileUpload field with clear button
var wrapTarget = false;
function addDeleteBtnToFileUpload(target){
	var file_input_index = 0;
    $(target).each(function() {
        file_input_index++;
		wrapId = $(this).attr('id')+'_wrap_'+file_input_index
		wrapTarget = "#"+wrapId
        $(this).wrap('<div id='+wrapId+'</div>');
        $(this).before('<input style="vertical-align: top; margin-right:2px; padding:1px 3px;" class="btn" type="button" value="X" onclick="reset_html(\'#'+wrapId+'\')" />');
		console.warn('clear button added')
	});
}
//inputObj must be an HTML Object: use $()[0] to get HTML object form $() 
function updateThumb(thumbTarget, inputObj, clear) {
	console.warn('-start updateThumb with object: '+inputObj);
	
	//remove thumb size
	$(thumbTarget).removeAttr('width');
	$(thumbTarget).removeAttr('height');
	
	if (inputObj.success){ 
		//update thumb for uImage change
		thumbUrl = inputObj.tmpUrl;
		$(thumbTarget).attr("src", thumbUrl)
		console.warn('updated thumb with new uImage: '+thumbUrl)
	}else{
		//update thumb for url change 
		thumbUrl = inputObj.value;
		$(thumbTarget).attr("src", thumbUrl);
		console.warn('updated thumb with new url: '+thumbUrl)
	}
	if (clear){
		console.warn('start clear')
		//clear imgUrl or uImage when other is updated
		oldVal = $(clear).attr("value");
		$(clear).attr("value", null);
		newVal = $(clear).attr("value");
		console.warn('end clear result: '+clear+' oldVal: '+oldVal+' newVal: '+newVal)
		console.warn('-end updateThumb')
	}
	
}
//clear image upload filed
function reset_html(clear) {
	console.warn('reset html for: '+clear)
    $(clear).html($(clear).html());
	onFileChange()
	console.warn('id_imgUrl.value: '+$('#id_imgUrl').attr("value"))
	if ($('#id_imgUrl').attr("value") == "") {
		$('#thumb_id').attr("src", cUrl);
		$('#id_imgUrl').attr("value", cUrl);
	}
}
function uImageDelete(fileName) {
	var jqxhr = $.post('/ajax/thumb/'+fileName, function() {
      console.warn('ajax del success: '+fileName);
    })
    .success(function() { console.warn('ajax del success2'); })
    .error(function() { console.warn('ajax del error'); })
    .complete(function() { console.warn('ajax del complete'); });
}
function cancelNewPin(){			
	if (prevUpload){
		uImageDelete(prevUpload);
	}
	prevUpload = false;
	//remove previous item from list
	$('.qq-upload-list').children().remove()
	//get default image
	$(thumbTarget).attr("src", '/static/core/img/thumb-default.png');
}