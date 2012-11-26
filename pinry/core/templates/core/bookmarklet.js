javascript : var baseurl = "{{ BASE_URL }}";(function () { 
	console.warn('--start bookmarklet--');
	{% load static %}
	////test for EXISTING bookmarklet
	if (document.getElementById("overlay") == undefined) {
		var d = document;
		var b = d.body;
		var o;
		var jq;
		////create overlay div
		o = d.createElement("div");
		o.setAttribute("id", "overlay");
		o.innerHTML += '{% spaceless %}{% include "pins/bmbase.html" %}{% endspaceless %}';
		////add jquery to overlay
		jq = d.createElement("script");
		jq.type = "text/javascript";
		jq.src = "{{ BASE_URL }}/static/vendor/jquery/1.7.2/jquery.js";
		o.appendChild(jq);
		////add modal backdrop to overlay
		mbd = d.createElement("div");
		mbd.setAttribute("id", "backdrop");
		o.appendChild(mbd)
		////add overlay to etxternal site
		b.appendChild(o);
		console.warn('overlay added');
		//check for jquery
		checkLoad("window.$", jqReady, "jquery has loaded");
	}else {
		alert("You have an open bookmarklet already!");		
	}
	//exicute when jquery is ready
	function jqReady() {
        console.warn('--jqReady exicuted');
		bs = d.createElement("script");
		bs.type = "text/javascript";
		bs.src = "{{ BASE_URL }}/static/vendor/bootstrap/2.0.3/js/bootstrap.js";
		d.getElementById("overlay").appendChild(bs);
		//check for bootstrap.js
	
        console.warn('--bdReady exicuted');
		s4 = d.createElement("script");
		s4.type = "text/javascript";
		s4.src = "{{ BASE_URL }}/static/core/js/ajaxform.js";
		d.getElementById("overlay").appendChild(s4);
		console.warn('ajaxform.js added');
		////populate form with data
		d.getElementById("id_imgUrl").setAttribute("value", "{{ imgUrl }}");
		////set form action url to ajaxsubmit view
		d.getElementById("ajaxform").setAttribute("action", baseurl+"/ajax/submit/");
		////display modal form & background
		//$('#new-pin').modal('toggle');//works chrome not ie10 use below code until ie10 issue resolved
		b.setAttribute("class", "modal-open");
        mbd.setAttribute("class", "modal-backdrop fade in");
		d.getElementById("new-pin").setAttribute("class", "modal fade in");
		console.warn('--end bookmarklet--');
	}
	//Check Tool
	function checkLoad(test, callback, msg) {
		console.warn("--test--"+test)
		if(eval(test)) {
			console.warn("--pass--");
			callback();
		} else {
			console.warn("--retest--")
			window.setTimeout(function(){checkLoad(test, callback, msg)}, 15 );
		}
	}
}());
