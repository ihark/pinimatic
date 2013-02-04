/**
 * Based on Wookmark's endless scroll.
 */
var apiURL = '/api/v1/pin/?format=json&offset='
//var favsURL = '/api/v1/favs/?format=json&'
var userURL = '/api/v1/auth/user/?format=json&'
var page = 0;
var handler = null;
var cTag = null;//used to track current tag
var cTags = null;//not used yet for list of current tag filters
var cUser = null;//used to track current user
var isLoading = false;
var pinsUrl = "" //url required for access to pins url's (defined in pinry.urls for include: pinry.pins.urls)
var apiPrefixA = ["user", "profile"]//prefix for recent-pins (defined in pins.urls recent-pins) determines when to use pins api in below funcions
var authUser = $('#user').attr('data-user')
console.log('current authUser: '+authUser)
//TODO: need to get current athenticated user as java variable

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
      handler = $('#pins-container .pin');
      handler.wookmark({
          autoResize: true,
          offset: 3,
          itemWidth: 242
      });
	  $('#user-info').show();
  });
};

/**
 * Loads data from the API. 
 * tag set by tag click user set by nav bar button)
 * set tag / user to null to clear
 */
//reloads page on state change 
window.onpopstate = function(e) {
	console.warn('pop state: '+e.state);
	//alert("location: " + document.location + ", state: " + JSON.stringify(event.state));
	if (e.state) window.location.href = e.state;
};
function inArray(value, array){
	var i;
	for (i=0; i < array.length; i++) {
		if (array[i] === value) {
			return value;
		}
	}
	return false;
}
function loadData(tag, user) {
    isLoading = true;
    $('#loader').show();
	var apiPrefix = inArray(url(1), apiPrefixA);
	console.warn('first user: '+user);
	console.warn('first Tag: '+tag);
	
	//check url for current user / tag
	if (url(2) && apiPrefix) {
		console.warn('url(2)sets cUser to: '+url(2));
		cUser = url(2);
		var nAddress = '/'+apiPrefix+'/';
	}
	if (url(3) && apiPrefix) {
		console.warn('url(3) sets cTag to : '+url(3));
		cTag = url(3);
    }else{
		cTag = null;
	}
	
	//determine if new user or tag selected and set url to current if not except if null.
	if (user) {
		nAddress += user+'/';
		console.warn('if user update url to: '+nAddress);
	}else if (cUser) {
		user = cUser;
		nAddress += user+'/';
		console.warn('else if cUser update url to: '+nAddress);
	}
	if (tag){//*add support for multi tags with cTags, maybe peramiter url is better??
		nAddress += tag+'/';
		console.warn('if tag update url to: '+nAddress);
	}else if (cTag && tag !== null){
		tag = cTag;
		nAddress += cTag+'/';
		console.warn('else if cTag update url to: '+nAddress);
	}
	if (tag){
		$('#tags').html('<span class="label tag" onclick="loadData(null)">' + tag + ' x</span>');
	}else{
		$('#tags').html('');
	}
	//window.location.href = nAddress
	console.warn('final url = '+nAddress);
	console.warn('url(path) = '+url('path'));
	if (nAddress && nAddress != url('path')){
		console.warn('PUSH STATE ADDED');
		window.history.pushState(nAddress, 'Pinry: '+nAddress, nAddress);
	}
	
	
	//reset page and refresh pins display
	if (tag !== undefined || user !== undefined && user !== cUser){
		page = 0;
		$('#pins').html('');
	}
   
	console.warn('page: '+page);
    var loadURL = apiURL+(page*30);
	console.warn('final user: '+user);
	console.warn('final tag: '+tag);
	if (user && user != 'all') loadURL += "&user=" + user;
    if (tag && tag !== null) loadURL += "&tag=" + tag;
	
	//prevent api request when not in apiPrefix domain
	if (url(1) == apiPrefix) {
		$.ajax({
			url: loadURL,
			contentType: 'application/json',
			beforeSend: function(jqXHR, settings) {
				jqXHR.setRequestHeader('X-CSRFToken', $('input[name=csrfmiddlewaretoken]').val());
			},
			success: onLoadData,
			error: function(jqXHR, settings) {
				console.warn('ladData - ajax error');
			},
		});
	}
};

/**
 * Receives data from the API, creates HTML for images and updates the layout
 */
function onLoadData(data) {
	data = data.objects;
	//getFavData(image.id)
	page++;
	
	var userFav
	var i=0, length=data.length, image;
	for(; i<length; i++) {
		image = data[i];
		userFav = false
		var html = '';
		for (f in image.favorites){
			if (image.favorites[f].user == authUser){
				userFav = true;
				break
			}
		}
		html += '<div class="pin" id="'+image.id+'-pin" data-favs="'+image.favorites.length+'">';
			html += '<div class="pin-options">';
				html += '<a href="'+pinsUrl+'/delete-pin/'+image.id+'/">';
				html += '<i id="delete-btn" title="Delete" class="icon-trash"></i>';
				html += '</a>';
				html += '<a href="'+pinsUrl+'/edit-pin/'+image.id+'/">';
					html += '<i id="edit-btn" title="Edit" class="icon-edit"></i>';
				html += '</a>';
				html += '<a>';
				if (userFav) {
					html += '<i id="favs" data-state="'+userFav+'" title="Remove Favorite" class="icon-star"></i>';
				} else {
					html += '<i id="favs" data-state="'+userFav+'" title="Add Favorite" class="icon-star-empty"></i>';
				};
				html += '</a>';
			html += '</div>';
			html += '<a class="fancybox" rel="pins" href="'+image.image+'">';
				html += '<img src="'+image.thumbnail+'" width="200" >';
			html += '</a>';
			html += '<div class="pin-info">';
				html += '<a class="pin-src" rel="pins" href="'+image.srcUrl+'">Posted from</a>';
					html += '<span class="text"> : by </span>'
				html += '<a class="pin-submitter" href="/user/'+image.submitter.username+'/">'+image.submitter.username+'</a>';
				html +='<span class="pin-stats pull-right">'
					html += '<i class="display icon favs"></i><span class="display text favs ">'+image.favorites.length+'</span>';
				html +='</span>'
			html += '</div>';
			html += '<div class="pin-desc">';
				if (image.description) html += '<p id="desc">'+image.description+'</p>';
			html += '</div>';
			html += '<div class="pin-tags">';
				if (image.tags) {
					html += '<p>';
					for (tag in image.tags) {
						html += '<span class="label tag" onclick="loadData(\'' + image.tags[tag] + '\')">' + image.tags[tag] + '</span> ';
					}
					html += '</p>';
				}
			html += '</div>';
		html += '</div>';
		$('#pins').append(html);
		//hide favs display if there are none
		if (!image.favorites[0]) $('#'+image.id+'-pin .display.favs').hide()
	}
	applyLayout();
	isLoading = false;
	$('#loader').hide();
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
 * Pin Options Functions.
 */

// add event listeners
$('#followers').live('click', function(event){
	follow(this)
});
$('#favs').live('click', function(event){
	togglePinStat(this, 'icon-star', 'icon-star-empty', '/toggle/pins/Pin/');
});
//TODO: may not need this or its not working
$('#user').live('onchange', function(event){
	authUser = this.attr('data-user')
	console.log('user changed to: '+authUser+this)
});


//TODO: make an ajax api function to consolodate all the ajax calls
//TODO: make one funtion to update all fav follow counts
/* togglePinStat: 
xxx: is a unique name of the stat to toggle
targetBtn: the HTML element acting as the toggle button
  must have: id="xxx" set staticly by onLoadData
  must have: data-state="true/false" current state of the toggle set dynamicly by onLoadData 
.pin class:  id=#-Pin, data-xxx=Current qty of stat
.display .*** .text: dispay's the current count
.display .*** .icon-iconname: display's the icon (must be 11px X 11p)
*/

function togglePinStat(targetBtn, tIcon, fIcon, url){
	console.log(targetBtn);
	var button = $(targetBtn);
	var name = button.attr('id');
	console.log('name: '+name);
	var state = button.attr('data-state');
	var pin = $($(targetBtn).closest(".pin"));
	console.log(pin);
	var id = parseInt(pin.attr('id'));
	console.log(id);
	var count = pin.attr('data-'+name);
	console.log(count);
	var disp = pin.find('.display.'+name);
	var dispText = pin.find('.display.text.'+name);
	console.log(disp);
	var aProfile = $('.pin.profile');
	console.log(aProfile);
	var countP = aProfile.attr('data-'+name);
	console.log(count);
	var dispTextP = aProfile.find('.display.text.'+name);
	var aProfileId = aProfile.attr('data-profile')
	console.log(aProfileId);
	if (authUser == aProfileId) {
		console.log('authUser = aProfile');
		var updateProfile = true;
	}

	this.onFav = function( result ) {
		if (state == "true"){
			count--;
			countP--;
			button.attr('data-state', "false");
			button.addClass(fIcon);
			button.removeClass(tIcon);
			pin.attr('data-'+name, count);
			dispText.html(count);
			if (count == 0) {
				disp.hide();
			}
			if (updateProfile){
				aProfile.attr('data-'+name, countP);
				dispTextP.html(countP);
			}
		}else{
			count++;
			countP++;
			button.attr('data-state', "true");
			button.addClass(tIcon);
			button.removeClass(fIcon);
			pin.attr('data-'+name, count);
			dispText.html(count);
			disp.show();
			if (updateProfile){
				aProfile.attr('data-'+name, countP);
				dispTextP.html(countP);
			}
		}
	}
	
	$.ajax({
		url: pinsUrl+url+id+'/',
		type: 'POST',
		contentType: 'application/json',
		beforeSend: function(jqXHR, settings) {
			jqXHR.setRequestHeader('X-CSRFToken', $('input[name=csrfmiddlewaretoken]').val());
		},
		success: $.proxy(this.onFav, this),//TODO: swap fav image
		error: function(jqXHR, settings) {
			console.warn('addfav - ajax error');
		},
	});
}

function follow(targetBtn) {
	var button = $(targetBtn);
	var name = button.attr('id')
	var state = button.attr('data-state');
	var pin = $($(targetBtn).closest(".pin"));
	var id = parseInt(pin.attr('id'));
	var count = pin.attr('data-'+name);
	var disp = pin.find('.display.'+name)
	var dispText = pin.find('.display.text.'+name)

	this.onFollow = function( result ) {
		console.log('onFollow', result);
		// Update the number of followers displayed.
		console.warn('count: '+count)
		console.warn('state = '+state)
		if(state == "true") {
			button.attr('data-state', 'false');
			button.html('Spy')
			count--;
			console.warn('count: '+count)
			//this.showLoader('Liking');
		} else {
			button.attr('data-state', 'true');
			button.html('Un-Spy')
			count++;
			console.warn('count: '+count)
			//this.showLoader('Unliking');
		}
		pin.attr('data-'+name, count);
		dispText.html(count);
	};
	
	var url = pinsUrl+'/toggle/auth/User/'+id+'/';
	$.ajax({
		url: url,
		type: 'POST',
		contentType: 'application/json',
		beforeSend: function(jqXHR, settings) {
			jqXHR.setRequestHeader('X-CSRFToken', $('input[name=csrfmiddlewaretoken]').val());
		},
		success: $.proxy(this.onFollow, this),//todo: need to detect if followed or not
		error: function(jqXHR, settings) {
			console.warn('follow - ajax error');
		},
	});
}
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