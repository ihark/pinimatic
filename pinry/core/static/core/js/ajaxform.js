console.warn('ajaxform.js has exicuted: waiting for doc ready');
$(document).ready(function () {
	console.warn('ajax form document ready');
	var messageListName = 'messageList';
	////ajax submit
	$('#ajaxform').submit(function () { //// catch the form's submit event
		var csrfToken = 'placeholder';
		$.ajax({ //// create an AJAX call...
			data : $(this).serialize(), //// get the form data
			dataType : "json",
			type : $(this).attr('method'), //// GET or POST from method attribute
			url : $(this).attr('action'), //// url from method attribute
			headers:  {
			'x-requested-with' : 'XMLHttpRequest' //// add header for django form.is_valid() 
			},
			xhrFields: {
			withCredentials: true //// add credentials to the request
			},
			beforeSend : function(xhr, settings) {
				////shold only be used with SSL get CSRF Token & add to headder or use basic auth
				////xhr.setRequestHeader("X-CSRFToken", $('#csrfmiddlewaretoken').val());
				////xhr.setRequestHeader("Authorization", "user:pass");
				clearMessages(messageListName);
				clear_form_field_errors('#ajaxform');
			},
			success : function (data, textStatus, xhr) { // on success..
				var contentType = xhr.getResponseHeader("Content-Type");
				if (contentType == "application/javascript" || contentType == "application/json") {
					var jsonMessage = $.parseJSON(xhr.responseText);
					$.each(jsonMessage, function(index, value) {
						if (index === "django_messages") {
							$.each(jsonMessage.django_messages, function (i, item) {
								addMessage(messageListName, item.message, item.extra_tags);
								////if success message
								if (item.extra_tags == "alert alert-success"){
									$("#cancel").text("Close");
									$("#btnsubmit").remove();
								////if not logged in
								} else if (item.extra_tags.indexOf('login') > -1){
									//chrome requires return false in submit or it crashs
									//$("#ajaxform").attr( 'onsubmit', 'popForm(this)' );
									//$("#ajaxform").attr( 'action', "http:"+baseurl+"/pins/new-pin/");
									$("#btnsubmit").text('LogIn');
									$('#ajaxform').unbind('submit').find('input:submit,input:image,button:submit').unbind('click');
									$('#ajaxform').submit(function () {
										data = $("#ajaxform").serialize()
										popLoc(data);
										removeOverlay();
										return false;
									});
								}
							});
						////handle general form errors
						} else if (index === "__all__") {
							$.each(jsonMessage.__all__, function (i, item) {
								addMessage(messageListName, item.message, item.extra_tags);
							});
						////handle form field errors
						} else {
							$.each(jsonMessage[index], function (i, item) {
								apply_form_field_error(index, item.message, item.extra_tags);
							});
						}
					});
                }
			},
			error : function(xhr, textStatus, errorThrown) {
				console.warn("error: xhr.status: "+xhr.status+" / textStatus: "+textStatus);
				addMessage(messageListName,"There was an error connectiong to the server, please try again later.", "alert alert-error");
            },
		});
		return false;
	});
});
////this method requires default submit function which is broken in chrome due to injection of from after dom loaded
// function popForm(form) {
	// nw = window.open("", 'formpopup', 'width=800,height=400,resizeable,scrollbars');
	// form.target = 'formpopup';
	// if (window.focus) {
		// nw.focus()
	// }	
// }
function popLoc(data) {
	//&mode=save tells view to save pin in lew of POST
	nw = window.open("http:"+baseurl+"/new-pin/?"+data+"&save=True", 'popup', 'width=800, height=400, resizeable=true, scrollbars');
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
    var message = $('<li id="message" class="'+extra_tags+' alertSmall" style="crap" >'+text+'</li>').hide();
	$( '#'+html_id ).prepend(message);
	//message.insertAfter(id);
    message.fadeIn(500);
    // setTimeout(function() {
        // message.fadeOut(2000, function() {
            // message.remove();
        // });
    // }, 10000);
}
function apply_form_field_error(fieldname, error, tags) {
    var input = $( "#id_"+fieldname+"_label"),
        container = $( "#div_id_"+fieldname),
        error_msg = $("<span />").addClass("help-inline ajax-error").text(error);

    container.addClass("error");
    error_msg.insertAfter(input);
}
function clear_form_field_errors(form) {
    $(".ajax-error", $(form)).remove();
    $(".error", $(form)).removeClass("error");
}