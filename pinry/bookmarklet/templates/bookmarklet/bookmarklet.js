javascript :var baseurl = "{{ US_SITE_URL }}";
			var authUserO = {{ auth_user_o|safe }};
			var apiURL = "{{ API_URL }}";
			var viud="{{ csrftoken }}";
			var staticPrefix="{{STATIC_PREFIX}}";
			(function () { 
	console.warn('--start bookmarklet--');
	{% load static %}
	////test for EXISTING bookmarklet or siteDom domain
	siteDom = /^https?:\/\/.*?(({{site_name|lower}})|({{site_name|lower}}-t)|(localhost)).*?\//
	//prevent base page from scrolling
	document.body.style.overflow = "hidden"
	insiteDom = location.href.match(siteDom);
	console.warn('test for siteDom host : '+insiteDom)
	if (document.getElementById("overlay") == undefined && insiteDom == null) {
		////find all images on page and create golbal variables
		var d = document;
		var b = d.body;
		var images = d.getElementsByTagName("img");
		var iq = images.length;
		var ii = 0;
		var il = 0;
		var io = [];
		var data = {};
		var buttons = {};
		window.lsp = {
			x : document.all ? document.scrollLeft : window.pageXOffset,
			y : document.all ? document.scrollTop : window.pageYOffset
		};
		////add css
		function appendStyle(styles) {
			var css = document.createElement('style');
			css.type = 'text/css';

			if (css.styleSheet) css.styleSheet.cssText = styles;
			else css.appendChild(document.createTextNode(styles));

			o.appendChild(css);
			}

		var styles = '#overlay .modal-backdrop.fade {opacity: 0;-webkit-transition: opacity 1s linear;-moz-transition: opacity 1s linear;-o-transition: opacity 1s linear;transition: opacity 1s linear;}';
		styles += '#overlay .modal-backdrop.fade.in {opacity:.9;filter: alpha(opacity=90);}';
		
		////create overlay div
		var o = d.createElement("div");
		o.setAttribute("id", "overlay");
		os = "position:absolute; top:0px; left:0px; right:0px; bottom:0px; z-index:900000000000000000000000000;"
		setStyles(o, os)
		b.appendChild(o);// append overlay to document body
		console.warn('overlay added');
		////append styles
		appendStyle(styles);
		

		////create modal backdrop
		var mbd = d.createElement("div");
		mbd.setAttribute("id", "backdrop");
		mbd.setAttribute("class", "modal-backdrop fade");
		var mbds = "z-index: -1; position: fixed; top: 0;right: 0;bottom: 0;left: 0;";
		mbds += "background-color: #000000;";
		setStyles(mbd, mbds)
		o.appendChild(mbd);// append background to overlay
		console.warn('modal-backdrop added');
		mbd.className += " in";
		
		
		//load jquery
		loadScript("vendor/jquery/1.7.2/jquery.js", "jQuery.fn.jquery", jqReady, "1.7.2");
		
		////create loader
		var lo = d.createElement("div");
		lo.setAttribute("id", "loader");
		var los = "z-index: 100; position: fixed; top: 50%;right: 50%; text-align:center;";
		setStyles(lo, los)
		o.appendChild(lo);// append loader
		var loi = d.createElement("img");
		loi.src = "{{ STATIC_PREFIX }}{{ STATIC_URL }}core/img/loader.gif"
		lo.appendChild(loi)//append image to loader div
		var lot = d.createElement("div");
		lot.innerHTML = "loading"
		lo.appendChild(lot)//append text to loader div
		console.warn('loader added');

		////add overlay content
		innerHTML = '{% spaceless %}{% include "pins/bmbase.html" %}{% endspaceless %}';
		//apped all occurances of /static/ in the bmbase template with staticPrefix
		o.innerHTML += innerHTML.replace(/\/static\//g,staticPrefix+"/static/")
		
		////create header
		var hh = "30";
		//hg eliminates possible jitter on fixed header
		var hc = d.createElement("div")
		hc.setAttribute("id", "header-bg");
		var hcs = "z-index: 10; width: 100%; position: absolute; top: 0; left: 0;";
		setStyles(hc, hcs);
		o.appendChild(hc);
		var h = d.createElement("div")
		h.setAttribute("id", "header");
		var hs = "z-index: 10; min-width: 500px; width: 100%; height: "+hh+"px; position: fixed; left: 0; top: 0; background-color: white;";
		setStyles(h, hs);
		hc.appendChild(h);// append header to header container
		var mh = d.createElement("div");
		mhs = "line-height:"+hh+"px; cursor: default; display: inline-block; float:left; background-color: transparent; padding: 0 0 0 20px; line-height: "+hh+"px;";
		setStyles(mh, mhs);
		h.appendChild(mh);//append message & logo to header
		var l = d.createElement("span");
		l.setAttribute("class", "brand")
		l.setAttribute("id", "header-b");
		ls = "line-height:"+hh+"px; cursor: pointer; display: inline-block; float:left; background-color: transparent; text-indent: 0px; margin 0;";
		ls += "font-size: 18px; color: #333; font-family: 'Fugaz One'; padding: 0 10px 0 0; cursor: pointer;";
		setStyles(l, ls);
		l.innerHTML = "{{site_name}}";
		l.onclick = delegate(onClickLogo, this);
		mh.appendChild(l);//append logo to mh
		var m = d.createElement("span");
		m.setAttribute("id", "header-m");
		ms = "line-height:"+hh+"px; display: inline-block; float:left; background-color: transparent; text-indent: 0px;";
		ms += "font-size: 13px; color: #black; font-family: Helvetica, arial, sans-serif; font-weight: normal; padding:0;";
		setStyles(m, ms);
		m.innerHTML = "Select an image to pin.";
		mh.appendChild(m); //append message to mh
		var nc = d.createElement("ul");
		ncs = "margin:0; float:right; border-left: 1px solid #CCC; color: #333; text-shadow: none; padding: 0px 20px; display: block; font-size: 13px; list-style: none; cursor: pointer;";
		setStyles(nc, ncs);
		h.appendChild(nc);//append nav to header
		var n1 = d.createElement("li");
		ns = "line-height:"+hh+"px;"
		n1.innerHTML = "Close"
		setStyles(n1, ns);
		n1.onclick = delegate(removeOverlay, this);
		nc.appendChild(n1);//append nav 1 to header

		

		////create image grid container
		var igs = d.createElement("div");
		igs.setAttribute("id", "image-grid-scroller");
		igss = "overflow-x:hidden; overflow-y:scroll; position:fixed; left:0px; right:0px; bottom:0px; clear:both; top:"+hh+"px;"
		setStyles(igs, igss);
		o.appendChild(igs);// append image grid container to overlay
		var igc = d.createElement("div");
		igc.setAttribute("id", "image-grid-container");
		igcs = "z-index:0; text-align: center; margin: 0 0 0 0; position: relative; top: 0";
		setStyles(igc, igcs);
		igs.appendChild(igc);// append image grid container to overlay
		

		////find images
		fni();
	}else {
		if (insiteDom) {
			alert("You have already added everything here to {{site_name}}.  Try going to a page outside {{site_name}} to find new pins!");
		}
	}
	//load other scripts
	function jqReady() {
		loadScript("vendor/bootstrap/2.2.2/js/bootstrap.js", "jQuery.fn.modal", bootstrapReady);
	}
	function bootstrapReady() {
		$.ui=''
		loadScript("vendor/jquery-ui/1.10.2.custom/js/jquery-ui-1.10.2.custom.js", "$.ui.version", jqueryuiReady, "1.10.2");
	}
	function jqueryuiReady() {
		jQuery.ui.tagit=''
		loadScript("vendor/jquery-ui-tag-it/js/tag-it.js", "jQuery.ui.tagit", tagitReady);
	}
	function tagitReady() {
		loadScript("core/js/ajaxform.js", "$.fn.exists", ajaxformReady);
	}
	function ajaxformReady() {
		////set form action url to ajaxsubmit view
		d.getElementById("ajaxform").setAttribute("action", baseurl+"/ajax/submit/");
		////remove loader
		o.removeChild(d.getElementById("loader"));
		////scroll to top of page
		window.scrollTo(0, 0);//scroll to top of page
		//use below only if you need to open modal on page load
		//$('#form-container').modal('toggle');    //works chrome not ie10
		//d.getElementById("form-container").setAttribute("class", "modal fade in"); //works all browsers
		console.warn('--end bookmarklet--');
		/* $('document').jScrollPane(
			{autoReinitialise: true}
		); */
	}
	
	
	//image grid functions
	function fni() {
			//console.warn('fni entered');
			if (ii < iq) {
				var e = cni(images[ii]);
				if (e) {
					il++
				}
				ii++;
				setTimeout(delegate(fni, this), 10)
			} else if (il == 0) {
				window.alert("Sorry, could not find any images to pin.");
				removeOverlay()
			}
			else { //do when no images remain
				//IOS fix overflow:scroll errors
				var scrollable = document.getElementById("image-grid-scroller");
				new ScrollFix(scrollable);
				
			}
		};
	function cni(e) {
		//console.warn('cni for: '+e.src);
		var t = false;
		if (e.src.match(siteDom)) {
			//console.warn('--image skiped: in siteDom domain--');
			return t
		} else {
			if (e.width < 150 && e.height < 150 || e.width < 100 && e.height < 20) {
				//console.warn('--image skiped: too small--');
				return t
			}
			if (e.src.match(/\.(tif|tiff|bmp)$/i)) {
				//console.warn('--image skiped: wrong img type--');
				return t
			}
			t = true;
			ani(e)
		}
		return t
	};
	function ani(e) {
		//console.warn('ani entered');
		var gi = d.createElement("div");
		var gis = "display: inline-block; width: 200px; height: 200px; margin: 15px; position: relative; overflow: hidden;";
		gi.className = "imageGrid";
		gi.id = "image_" + io.length;
		setStyles(gi, gis);
		var iw = e.width;
		var ih = e.height;
		var iwm = Math.min(iw, 200);
		var ihm = Math.min(ih, 200);
		var iaw = iwm / iw;
		var iah = ihm / ih;
		if (iaw < iah) {
			ihm = ih * iaw
		} else {
			iwm = iw * iah
		}
		var pw = Math.round((200 - iwm) / 2);
		var ph = Math.round((200 - ihm) / 2);
		var ic = d.createElement("div");
		ics = "display: table; vertical-align: middle; position: relative;";
		ics += "padding: " + ph + "px 0 0 " + pw + "px;";
		setStyles(ic, ics);
		var i = d.createElement("img");
		is = "-moz-box-shadow: 0 2px 12px rgba(0,0,0,.75); -webkit-box-shadow: 0 2px 12px rgba(0,0,0,.75); box-shadow: 0 2px 12px rgba(0,0,0,.75); display: inline-block;";
		setStyles(i, is);
		i.src = e.src;
		i.width = iwm;
		i.height = ihm;
		i.title = iw + "x" + ih;
		var ib = d.createElement("div");
		ibs = "width: " + iwm + "px; height: " + ihm + "px; position: absolute; top: " + ph + "px; left: " + pw + "px; opacity: 0; line-height: " + ihm + "px; text-align: center; font-weight: bold; color:#ffffff;";
		ibs += "background: url('http://www.wookmark.com/assets/bk_shader.png'); font-size: 18px; text-shadow: 0 1px 3px rgba(0,0,0,.75); font-family: Helvetica, arial, sans-serif;";
		ibs += "-webkit-transition: all 0.2s ease-out; -moz-transition: all 0.2s ease-out; -ms-transition: all 0.2s ease-out; -o-transition: all 0.2s ease-out; transition: all 0.2s ease-out;";
		ibs += "cursor: pointer;";
		ib.innerHTML = "Save image";
		ib.title = iw + "x" + ih;
		setStyles(ib, ibs);
		ic.appendChild(i);
		gi.appendChild(ic);
		gi.appendChild(ib);
		igc.appendChild(gi);
		gi.onclick = delegate(onClickImage, this);
		gi.onmouseover = delegate(onMouseOverImage, this);
		gi.onmouseout = delegate(onMouseOutImage, this);
		data[gi.id] = e;
		//console.warn('ani: append data'+data[gi.id]);
		buttons[gi.id] = ib;
		io.push(gi)
		//console.warn('--ani complete added to grid:'+data[gi.id].src);
	};
	//Check script load Tool
	function loadScript(src, test, callback, testVersion) {
		var i = 0
		checkVersion = function (test, testVersion) {
			try{
				var pass = eval(test)
			}catch(err){
				var pass = false
			}
			
			if (pass && testVersion){
				pass = false
				if (typeof(testVersion) != 'number') {testVersion = Number(testVersion.replace('.',''))}
				version = Number(eval(test).replace('.',''))
				console.warn(version, '>=', testVersion)
				if (version >= testVersion){
					pass = true
				}
			}
			return pass
		}
		
		checkLoad = function (src, test, callback, testVersion) {
			pass = checkVersion (test, testVersion)
			if(pass) {
				console.warn("**LOADED:", src);
				callback();
			} else if (i<1000){
				i++
				console.warn("--test result: ", test, pass)
				window.setTimeout(function(){checkLoad(src, test, callback, testVersion)}, 15 );
			} else { 
				alert('{{site_name}}: The bookmarklet did not load properly.  Please refresh the page and try again.')
			}
		}

		pass = checkVersion(test, testVersion)
		if (!pass){
			s = d.createElement("script");
			s.type = "text/javascript";
			s.src = "{{ STATIC_PREFIX }}{{ STATIC_URL }}"+src;
			o.appendChild(s);
			console.warn('*Added: '+src);
			checkLoad(src, test, callback, testVersion)
		}else{
			callback();
		}
		
	}

	//utils
	function setStyles(e, t) {
			e.setAttribute("style", t);
			e.style.cssText = t
		};
	function getColumnCount() {
		var e = getDocWidth();
		var t = Math.floor(e / 230);
		return t
	};
	function delegate(e, t) {
		var n = function () {
			return e.apply(t, arguments)
		};
		return n
	};
	function getDocHeight() {
		return Math.max(Math.max(document.body.scrollHeight, document.documentElement.scrollHeight), Math.max(document.body.offsetHeight, document.documentElement.offsetHeight), Math.max(document.body.clientHeight, document.documentElement.clientHeight))
	};
	function getDocWidth() {
		var e = window;
		var t = "inner";
		if (!("innerWidth" in window)) {
			t = "client";
			e = document.documentElement || document.body
		}
		return e[t + "Width"]
	};
	//event handlers
	function onClickLogo() {
		var t = baseurl;
		window.open(t)
	};
	function onClickImage(e) {
		var i = normalizeEventTarget(e);
		var id = i.id;
		i = data[id];
		////use loop to see all attributes in console
		//for (a in i){
			//console.warn('a= '+a+' i[a]= '+i[a]);
		//}
		////populate form with data & make visable
		d.getElementById("form-container").setAttribute("style", "display: block;");//must be here to allow enough time for diplay change
		d.getElementById("id_srcUrl").setAttribute("value", "{{ srcUrl }}");
		d.getElementById("id_imgUrl").setAttribute("value", i.src);
		var t = d.getElementById("thumb_id");
		t.setAttribute("src", i.src);
		ts = "-moz-box-shadow: 0 2px 12px rgba(0,0,0,.75); -webkit-box-shadow: 0 2px 12px rgba(0,0,0,.75); box-shadow: 0 2px 12px rgba(0,0,0,.75); display: inline-block;";
		setStyles(t, ts);
		////display form
		o.removeChild(igs);
		//$('#form-container').modal('toggle')
		d.getElementById("form-container").setAttribute("class", "modal fade in");
		//prevent autocomplete list from moving on scroll
		$('.ui-autocomplete').css('position', 'fixed')
	};
	function onMouseOverImage(e) {
		var t = normalizeEventTarget(e);
		var n = data[t];
		var r = t.getElementsByTagName("div");
		var i = r[1];
		selectedImage = n;
		i.style.opacity = 1
	};
	function onMouseOutImage(e) {
		var t = normalizeEventTarget(e);
		var n = t.getElementsByTagName("div");
		var r = n[1];
		selectedImage = null;
		r.style.opacity = 0
	};
	function normalizeEventTarget(e) {
		if (window.event) {
			e = window.event
		}
		var t = e.currentTarget ? e.currentTarget : e.srcElement;
		while (t.className != "imageGrid" && t.parentNode) {
			t = t.parentNode
		}
		return t
	};
}());
//global functions
function removeOverlay() {
	var f = document.getElementById("form-container");
	f.setAttribute('class', 'modal fade');
	t = document.getElementById("overlay");
	document.body.removeChild(t);
	document.body.setAttribute("class", "");
	window.scrollTo(lsp.x, lsp.y);
	document.body.style.overflow = "auto"
}
/**
 * ScrollFix v0.1
 * http://www.joelambert.co.uk
 *
 * Copyright 2011, Joe Lambert.
 * Free to use under the MIT license.
 * http://www.opensource.org/licenses/mit-license.php
 */

var ScrollFix = function(elem) {
	// Variables to track inputs
	var startY, startTopScroll;

	elem = elem || document.querySelector(elem);

	// If there is no element, then do nothing	
	if(!elem)
		return;

	// Handle the start of interactions
	elem.addEventListener('touchstart', function(event){
		startY = event.touches[0].pageY;
		startTopScroll = elem.scrollTop;

		if(startTopScroll <= 0)
			elem.scrollTop = 1;

		if(startTopScroll + elem.offsetHeight >= elem.scrollHeight)
			elem.scrollTop = elem.scrollHeight - elem.offsetHeight - 1;
	}, false);
};