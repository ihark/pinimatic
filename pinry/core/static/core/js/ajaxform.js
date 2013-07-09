﻿//overide _create so tag is created when focus is lost
$.widget( "ui.tagit", $.ui.tagit, {
	_create: function() {
		this._super( "_create" );
		var that = this
		this.tagInput.blur(function(e){
			// Create a tag when the element loses focus.
			// If autocomplete is enabled and suggestion was clicked, don't add it.
			that.createTag(that._cleanedInput());
		});
	}
});
console.warn('ajaxform.js has exicuted: waiting for doc ready');
var messageDivId = 'messageList';
$(document).ready(function () {
	console.warn('ajax form document ready');

	////ajax submit
	$('#ajaxform').submit(function () { //// catch the form's submit event
		var csrfToken = 'placeholder';
		$.ajax({ //// create an AJAX call...
			context: $(this),
			data : $(this).serialize(), //// get the form data
			dataType : "json",
			type : $(this).attr('method'), //// GET or POST from method attribute
			url : $(this).attr('action'), //// url from method attribute
 			headers:  {
			'x-requested-with' : 'XMLHttpRequest' //// Required for cors with django, form validation and ajax messages , seems to be excluded from forms with file fields
			},
			xhrFields: {
			withCredentials: true //// enables xcrf validation with all but IE
			},
			beforeSend : function(xhr, settings) {
				////Only use with SSL! get CSRF Token & add to headder
				//xhr.setRequestHeader("X-CSRFToken", $('#csrfmiddlewaretoken').val()); //work arround for IE: gets cookie from from but problem with '' instad of "" used. TOTRY: put the cookie in the js instead.
				////Only use with SSL! manual authentication, last resort
				//xhr.setRequestHeader("Authorization", "user:pass");
				clearMessages(messageDivId);
				clear_form_field_errors('#ajaxform');
			},
			success : function (data, textStatus, xhr) { // on success..
				var jsonMessage = getMessages(xhr, $(this))
				$.each(jsonMessage, function(index, value) {
					if (index === "django_messages") {
						$.each(jsonMessage.django_messages, function (i, item) {
							////if success message
							if (item.extra_tags.search("alert-success")+1){
								$("#cancel").text("Close");
								$("#btnsubmit").remove();
							////if not logged in
							} else if (item.extra_tags.indexOf('login') > -1){
								$("#btnsubmit").text('LogIn');
								$('#ajaxform').unbind('submit').find('input:submit,input:image,button:submit').unbind('click');
								$('#ajaxform').submit(function () {
									data = $("#ajaxform").serialize()
									popLoc(data);
									removeOverlay();
									//chrome requires return false in submit or it crashes
									return false;
								});
							}
						});
					}
				});
			},
			error : function(xhr, textStatus, errorThrown) {
				console.warn("error: xhr.status: "+xhr.status+" / textStatus: "+textStatus);
				addMessage(messageDivId,"There was an error connectiong to the server: "+xhr.status, "alert alert-error");
            },
		});
		return false;
	});
//tagit settings
if (authUserO){tu = authUserO.id}else{tu = null};
	$('input[name="tags"]').tagit({
		availableTags: getTags(tu),
		placeholderText: 'add..',
	});
});
	//integrate focus css to ul box
	$('.tagit input').focus(function(event) {
		target = $(event.target).closest('ul');
		target.addClass('active');
	});
	$('.tagit input').focusout(function(event) {
		target = $(event.target).closest('ul');
		target.removeClass('active');
	});
	

////this method requires default submit function which is broken in chrome due to injection of from after dom loaded
// function popForm(form) {
	// nw = window.open("", 'formpopup', 'width=800,height=400,resizeable,scrollbars');
	// form.target = 'formpopup';
	// if (window.focus) {
		// nw.focus()
	// }	
// }

//get and process messages targetForm should be sent as $(targetForm)
function getMessages(xhr, targetForm, contentType){
	console.warn('*****get messages')
	if (contentType == undefined){
		contentType = xhr.getResponseHeader("Content-Type")
	}else{
		xhr = {responseText:xhr}
	}
	console.warn(contentType)
	if (contentType == undefined){contentType = "text"}
	if (contentType.indexOf("application/javascript") != -1 || contentType.indexOf("application/json") != -1) {
		try{
			console.log(xhr.responseText)
			var jsonMessage = $.parseJSON(xhr.responseText);
			$.each(jsonMessage, function(index, value) {
				if (index === "django_messages") {
					$.each(jsonMessage.django_messages, function (i, item) {
						console.log('django_messages: '+item.message)
						addMessage(messageDivId, item.message, item.extra_tags);
					});
				////handle general form errors
				} else if (index === "__all__") {
					$.each(jsonMessage.__all__, function (i, item) {
						console.log('__all__: '+item.message)
						addMessage(messageDivId, item.message, item.extra_tags);
					});
				////handle tastypie field errors for pin
				} else if (index === "pin") {
					$.each(jsonMessage.pin, function (i, item) {
						console.log('pin: '+item.message)
						//addMessage(messageDivId, item, "alert fade-out click");
						apply_form_field_error(targetForm, i, item, item.extra_tags);
					});
				////handle form field errors
				} else {
					$.each(jsonMessage[index], function (i, item) {
						apply_form_field_error(targetForm, index, item.message, item.extra_tags);
					});
				}
			});
		}
		catch(err){
			console.log('getMessages error: ',err)
		}
	}
	return jsonMessage
}
function popLoc(data) {
	//&save=True tells view to save pin without "POST"
	nw = window.open(baseurl+"/new-pin/?"+data+"&save=True", 'popup', 'width=800, height=400, resizeable=true, scrollbars');
	if (window.focus) {
		nw.focus()
	}	
}

//ajax messages
function addMessageList(div_id) {
    var container = $( '.messageContainer' );
	var list = $('<div id="'+div_id+'" ></div>');
	container.append(list);
	return $( "#messageList" );
}
function clearMessages(div_id) {
    $( '#'+div_id ).remove();
	addMessageList(div_id);
}
function addMessage(html_id, text, extra_tags) {
	if (extra_tags.search('click')+1){
		var message = $('<div class="'+extra_tags+'"><button type="button" class="close" data-dismiss="alert">x</button>'+text+'</div>').hide();
	}else{
		var message = $('<li class="'+extra_tags+'">'+text+'</li>').hide();
	}
	$( '#'+html_id ).prepend(message);
	//set message to fade in
    message.fadeIn(500);
	//run alertFade to determine if message should fade out automatically
	alertFade()
}
function apply_form_field_error(targetForm, fieldname, error, tags) {
	if ($("#div_id_"+fieldname).length == 0){
		//check for fieldnames appeded with _0 (Multiselect)
		fieldname = fieldname+"_0";
	}
	var input = targetForm.find( "#id_"+fieldname+"_label");
    var container = targetForm.find( "#div_id_"+fieldname);
    var error_msg = $("<span />").addClass("help-inline ajax-error").text(error);
    container.addClass("error");
    error_msg.insertAfter(input);
}
function clear_form_field_errors(form) {
    $(".ajax-error", $(form)).remove();
    $(".error", $(form)).removeClass("error");
}
//jquery ui & taggit
function getTags(user) {
	if (user){ 
		var tags = []
		onSuccess = function( data, ajaxStatus, xhr) {
			if (data.objects){
				for (t in data.objects){
					tags.push(data.objects[t].name)
				}
			}
			console.log(tags)
		}
		$.ajax({
			url: apiURL+'pintags/?user='+user,
			contentType: 'application/json',
			withCredentials: true,
			success: onSuccess,
			error: function(jqXHR, settings) {
				console.warn('getTags - ajax error');
			},
		});
		return tags
	};
}
//things to do when modal is activated
$('.modal').live('shown', function(e){
   //$('.ui-autocomplete').css('position', 'fixed')
   $('body').css('overflow', 'hidden')
});
//things to do when modal is activated
$('.modal').live('hide', function(e){
   //$('.ui-autocomplete').css('position', 'absolute')
   $('body').css('overflow', 'auto')
});
//util for checking if an element existis: return bool
$.fn.exists = function(){
    return jQuery(this).length > 0;
};
