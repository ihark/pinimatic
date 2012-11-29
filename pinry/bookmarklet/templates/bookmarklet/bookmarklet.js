javascript : var baseurl = "{{ BASE_URL }}";(function () { 
	console.warn('--start bookmarklet--');
	{% load static %}
	////test for EXISTING bookmarklet
	pinry = /^https?:\/\/.*?\.?pinry\.com\//;
	if (document.getElementById("overlay") == undefined || location.href.match(pinry == null)) {
		var d = document;
		var b = d.body;
		var jq;
		////find all images on page and create golbal variables
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
		////create overlay div
		var o = d.createElement("div");
		o.setAttribute("id", "overlay");
		os = "position: absolute; top: 0px; left: 0px; right: 0px; bottom: 0px; z-index:900000000000000000000000000;"
		setStyles(o, os)
		o.innerHTML += '{% spaceless %}{% include "pins/bmbase.html" %}{% endspaceless %}';
		b.appendChild(o);// append overlay to document body
		console.warn('overlay added');
		////create modal backdrop
		mbd = d.createElement("div");
		mbd.setAttribute("id", "backdrop");
		//mbd.setAttribute("class", "modal-backdrop");
		mbds = "z-index: -1; position: fixed; top: 0; right: 0; bottom: 0; left: 0; margin: 0;";
		mbds += "background-color: rgba(0, 0, 0, 0.9);";
		setStyles(mbd, mbds)
		o.appendChild(mbd);// append background to overlay
		console.warn('modal-backdrop added');
		////add jquery to overlay
		jq = d.createElement("script");
		jq.type = "text/javascript";
		jq.src = "{{ BASE_URL }}/static/vendor/jquery/1.7.2/jquery.js";
		o.appendChild(jq);
		
		////create header
		var hh = "48";
		//hg eliminates possible jitter on fixed header
		var hc = d.createElement("div")
		hc.setAttribute("id", "header-bg");
		var hcs = "z-index: 10; width: 100%; position: absolute; top: 0; left: 0;";
		setStyles(hc, hcs);
		o.appendChild(hc);
		var h = d.createElement("div")
		h.setAttribute("id", "header");
		var hs = "z-index: 10; width: 100%; height: "+hh+"px; position: fixed; left: 0; top: 0; background-color: white;";
		setStyles(h, hs);
		hc.appendChild(h);// append header to header container
		var mh = d.createElement("p");
		mhs = "cursor: default; display: inline-block; float:left; background-color: transparent; padding: 0 0 0 20px; line-height: "+hh+"px;";
		setStyles(mh, mhs);
		h.appendChild(mh);//append message & logo to header
		var l = d.createElement("span");
		ls = "cursor: pointer; display: inline-block; float:left; background-color: transparent; text-indent: 0px; margin 0;";
		ls += "font-size: 30px; color: #333; font-family: 'Monoton'!important; padding: 0 10px 0 0; cursor: pointer;";
		setStyles(l, ls);
		l.innerHTML = "Pinry";
		l.onclick = delegate(onClickLogo, this);
		mh.appendChild(l);//append logo to mh
		var m = d.createElement("span");
		ms = "display: inline-block; float:left; background-color: transparent; text-indent: 0px;";
		ms += "font-size: 13px; color: #black; font-family: Helvetica, arial, sans-serif; font-weight: normal; padding: 7px 0 0 0;";
		setStyles(m, ms);
		m.innerHTML = "Select an image to pin.";
		mh.appendChild(m); //append message to mh
		var nc = d.createElement("ul");
		nc.setAttribute("class", "nav pull-right");
		ncs = "border-left: 1px solid #CCC; color: #333; text-shadow: none; padding: 14px 20px 15px; display: block; font-size: 13px; list-style: none; cursor: pointer;";
		setStyles(nc, ncs);
		h.appendChild(nc);//append nav to header
		var n1 = d.createElement("li");
		n1.innerHTML = "Close"
		n1.onclick = delegate(removeOverlay, this);
		nc.appendChild(n1);//append nav 1 to header
		
		// var cb = d.createElement("p");
		// cbs = "display: inline-block; float:right; width: 38px; height: 38px; background: url('http://www.wookmark.com/assets/bk_close.png') no-repeat center center;";
		// cbs += "line-height: "+hh+"px; margin: 4px 10px 0 0; cursor: pointer; padding: 0;";
		// setStyles(cb, cbs);
		// cb.onclick = delegate(removeOverlay, this);
		// h.appendChild(cb);//append cancil button to header

		////create image grid container
		var igc = d.createElement("div");
		igc.setAttribute("id", "image-grid-container");
		igcs = "text-align: center; z-index: 0; margin: 0 0 25px 0px; position: relative; clear:both; top: "+hh+"px;";
		setStyles(igc, igcs);
		o.appendChild(igc);// append image grid container to overlay

		////find images
		fni();
		//check for jquery
		checkLoad("window.$", jqReady, "jquery has loaded");
	}else {
		alert("You have an open bookmarklet already!");		
	}
	//exicute when jquery is ready
	function jqReady() {
        console.warn('--jqReady');
		bs = d.createElement("script");
		bs.type = "text/javascript";
		bs.src = "{{ BASE_URL }}/static/vendor/bootstrap/2.0.3/js/bootstrap.js";
		d.getElementById("overlay").appendChild(bs);
        console.warn('bootstrap.js added');
		s4 = d.createElement("script");
		s4.type = "text/javascript";
		s4.src = "{{ BASE_URL }}/static/core/js/ajaxform.js";
		d.getElementById("overlay").appendChild(s4);
		console.warn('ajaxform.js added');
		////set form action url to ajaxsubmit view
		d.getElementById("ajaxform").setAttribute("action", baseurl+"/ajax/submit/");
		////scroll to top of page
		window.scrollTo(0, 0);//scroll to top of page
		//use below only if you need to open modal on page load
		//$('#form-container').modal('toggle');    //works chrome not ie10
		//d.getElementById("form-container").setAttribute("class", "modal fade in"); //works all browsers
		console.warn('--end bookmarklet--');
	}
	//image grid functions
	function fni() {
			console.warn('fni entered');
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
				//d.getElementById("form-container").setAttribute("class", "modal fade"); // activate modal fade
			}
		};
	function cni(e) {
		console.warn('cni for: '+e.src);
		var t = false;
		if (e.src.match(pinry)) {
			console.warn('--image skiped: in pinry domain--');
			return t
		} else {
			if (e.width < 150 && e.height < 150 || e.width < 80 || e.height < 80) {
				console.warn('--image skiped: too small--');
				return t
			}
			if (e.src.match(/\.(tif|tiff|bmp)$/i)) {
				console.warn('--image skiped: wrong img type--');
				return t
			}
			t = true;
			ani(e)
		}
		return t
	};
	function ani(e) {
		console.warn('ani entered');
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
		console.warn('ani: append data'+data[gi.id]);
		buttons[gi.id] = ib;
		io.push(gi)
		console.warn('--ani complete added to grid:'+data[gi.id].src);
	};
	//Check script load Tool
	function checkLoad(test, callback, msg) {
		console.warn("--load test--"+test)
		if(eval(test)) {
			console.warn("--load pass--");
			callback();
		} else {
			console.warn("--load retest--")
			window.setTimeout(function(){checkLoad(test, callback, msg)}, 15 );
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
		o.removeChild(igc);
		d.getElementById("form-container").setAttribute("class", "modal fade in");
		console.warn('clicked image = '+i.src);
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
}