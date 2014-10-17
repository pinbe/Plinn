// (c) Benoît PIN 2006-2014
// http://plinn.org
// Licence GPL
// 
// 

var FormManager;

(function(){
	
FormManager = function(form, responseTextDest, lazy, noHistory) {
	if (form.elements.namedItem("noAjax")) {return;}
	
	this.form = form;
	this.responseTextDest = responseTextDest;
	this.lazy = lazy;
	this.noHistory = noHistory;
	var thisManager = this;
	this.form.onsubmit = function(evt) { thisManager.submit(evt); };
	this.form.onclick = function(evt) { thisManager.click(evt); };
	
	/* raised on form submit */
	this.onBeforeSubmit = null;
	/* raised after xmlhttp response */
	this.onResponseLoad = null;
	/* raised when the responseText is added inside the main element.
	 * (onResponseLoad may have the default value) */
	this.onAfterPopulate = null; 
	this.submitButton = null;
	
	if (this.lazy) {
		this.form.onclick = function(evt){
			thisManager.replaceElementByField(evt);
			thisManager.click(evt);
		};
		if (browser.isDOM2Event) {
			this.form.onfocus = this.form.onclick;
		}
		else if (browser.isIE6up) {
			this.form.onfocusin = this.form.onclick;
		}
		this.onResponseLoad = function(req){ thisManager.restoreField(req); };
		this.lazyListeners = [];
	}
};
	
FormManager.prototype.submit = function(evt) {
	var form = this.form;
	var thisManager = this;

	var bsMessage; // before submit message
	if (!this.onBeforeSubmit) {
		var onBeforeSubmit = form.elements.namedItem("onBeforeSubmit");
		if (onBeforeSubmit) {
			if (onBeforeSubmit.length) {
				onBeforeSubmit = onBeforeSubmit[0];
			}
			/*jslint evil: true */
			this.onBeforeSubmit = eval(onBeforeSubmit.value);
			bsMessage = this.onBeforeSubmit(thisManager, evt);
		}
	}
	else {
		bsMessage = this.onBeforeSubmit(thisManager, evt);
	}
	
	if (bsMessage === 'cancelSubmit') {
		try {disableDefault(evt);}
		catch (e){}
		return;
	}

	if (!this.onResponseLoad) {
		var onResponseLoad = form.elements.namedItem("onResponseLoad");
		if (onResponseLoad) {
			this.onResponseLoad = eval(onResponseLoad.value);
		}
		else {
			this.onResponseLoad = this.loadResponse;
		}
	}

	var submitButton = this.submitButton;
	var queryInfo = this.formData2QueryString();
	var query = queryInfo.query;
	this.hasFile = queryInfo.hasFile;
	
	
	if (!this.onAfterPopulate) {
		var onAfterPopulate = form.elements.namedItem("onAfterPopulate");
		if (onAfterPopulate) {
			this.onAfterPopulate = onAfterPopulate.value;
		}
		else {
			this.onAfterPopulate = function() {};
		}
	}
	
	if (submitButton) {
		query += submitButton.name + '=' + submitButton.value + '&';
	}
	
	if (form.method.toLowerCase() === 'post') {
		this._post(query);
	}
	else {
		this._get(query);
	}
	
	try {disableDefault(evt);}
	catch (e2){}
};

FormManager.prototype._post = function(query) {
	// send form by XmlHttpRequest
	query += "ajax=1";

	var req = new XMLHttpRequest();
	var thisManager = this;
	req.onreadystatechange = function() {
		switch (req.readyState) {
			case 1 :
				showProgressImage();
				break;
			case 4 :
				hideProgressImage();
				if (req.status === 200 || req.status === 204) {
					thisManager.onResponseLoad(req);
				}
				else {
					alert('Error: ' + req.status);
				}
				break;
		}
	};
	var url = this.form.action;
	req.open("POST", url, true);
	req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;charset=utf-8");
	req.send(query);
};

FormManager.prototype._get = function(query) {
	var url = this.form.action;
	url += '?' + query;
	AjaxLinkHandler.loadUrl(url);
};


FormManager.prototype.click = function(evt) {
	var target = getTargetedObject(evt);
	if(target.type === "submit" || target.type === "image") {
		this.submitButton = target;
		disablePropagation(evt);
	}
};

FormManager.prototype.replaceElementByField = function(evt) {
	evt = getEventObject(evt);
	var ob = getTargetedObject(evt);
	var eventType = evt.type;
	if (eventType === 'focus' || eventType === 'focusin') {
		if (this.liveFormField && ob.tagName !== 'INPUT') {
			this.pendingEvent = [ob, 'click'];
		}
		return;
	}
	var fieldName = ob.getAttribute('id');
	if (fieldName) {
		this.fieldTagName = ob.tagName;
		var tabIndex = ob.tabIndex;
		var text;
		if (ob.firstChild && ob.firstChild.className === 'hidden_value') {
			text = ob.firstChild.innerHTML;
		}
		else {
			text = ob.innerHTML;
		}
		disablePropagation(evt);
		var parent;
		thisManager = this;
		switch (ob.tagName) {
			case 'SPAN' :
				// create input element
				var inputText = document.createElement("input");
				inputText.setAttribute("type", "text");
				text = text.replace(/\n/g, ' ');
				text = text.replace(/\s+/g, ' ');
				text = text.replace(/^ /, '');
				text = text.replace(/ $/, '');
				inputText.setAttribute("value", text);
				var inputWidth = text.length / 1.9;
				inputWidth = (inputWidth > 5) ? inputWidth : 5;
				inputText.style.width = inputWidth + 'em';
				//inputText.setAttribute("size", text.length);

				// replacement
				parent = ob.parentNode;
				parent.replaceChild(inputText, ob);

				inputText.focus();
				inputText.select();
				inputText.setAttribute('name', fieldName);
				inputText.tabIndex = tabIndex;
				inputText.className = 'live_field';
				this.liveFormField = inputText;
				this.lazyListeners.push({'element': inputText, 'eventName' : 'blur', 'handler': function(){ thisManager.submit();}});
				this.lazyListeners.push({'element': inputText, 'eventName' : 'keypress', 'handler': function(evt){ thisManager._fitField(evt);}});
				this._addLazyListeners();
				break;

			case 'DIV' :
			case 'P' :
				// create textarea
				var ta = document.createElement('textarea');
				ta.style.display = 'block';
				ta.className = 'live_field';
				text = text.replace(/^\s*/, '');
				text = text.replace(/\s*$/, '');
				ta.value = text;

				// replacement
				parent = ob.parentNode;
				parent.replaceChild(ta, ob);

				ta.focus();
				ta.select();
				ta.setAttribute('name', fieldName);
				ta.tabIndex = tabIndex;
				this.liveFormField = ta;
				this.lazyListeners.push({'element': ta, 'eventName' : 'blur', 'handler': function(){ thisManager.submit();}});
				this._addLazyListeners();
				break;
		}
	}
};

FormManager.prototype._addLazyListeners = function() {
	var i, handlerInfo;
	for (i=0 ; i<this.lazyListeners.length ; i++) {
		handlerInfo = this.lazyListeners[i];
		addListener(handlerInfo.element, handlerInfo.eventName, handlerInfo.handler);
	}
};

FormManager.prototype._removeLazyListeners = function() {
	var i, handlerInfo;
	for (i=0 ; i<this.lazyListeners.length ; i++) {
		handlerInfo = this.lazyListeners[i];
		removeListener(handlerInfo.element, handlerInfo.eventName, handlerInfo.handler);
	}
};


FormManager.prototype.restoreField = function(req) {
	var text;
	var input = this.liveFormField;
	if (req.status === 200) {
		if (req.getResponseHeader('Content-Type').indexOf('text/xml') !== -1) {
			var out = '..........';
			if (req.responseXML.documentElement.firstChild) {
				out = req.responseXML.documentElement.firstChild.nodeValue;
			}
			
			switch (req.responseXML.documentElement.nodeName) {
				case 'computedField':
					text = out;
					break;
				case 'error':
					this._removeLazyListeners();
					alert(out);
					this.pendingEvent = null;
					input.focus();
					this._addLazyListeners();
					return false;
			}
		}
		else {
			text = req.responseText;
		}
	}
	else {
		text = '';
	}
	
	if (!text.match(/\w/)) {
		text = '..........';
	}
	
	var field = document.createElement(this.fieldTagName);
	field.innerHTML = text;
	field.setAttribute('id', input.getAttribute('name'));
	field.className = 'editable';
	field.tabIndex = input.tabIndex;
	
	var parent = input.parentNode;
	parent.replaceChild(field, input);
	this.liveFormField = null;
	
	if (this.pendingEvent) {
		raiseMouseEvent(this.pendingEvent[0], this.pendingEvent[1]);
	}
	return true;
};


FormManager.prototype.formData2QueryString = function() {
	// http://www.onlamp.com/pub/a/onlamp/2005/05/19/xmlhttprequest.html
	var form = this.form;
	var strSubmit = '', formElem, elements;
	var hasFile = false;
	var i;

	if (!this.lazy) {
		elements = form.elements;
	}
	else {
		elements = [];
		var formElements = form.elements;
		for (i = 0; i < formElements.length; i++) {
			formElem = formElements[i];
			switch (formElem.type) {
				case 'hidden':
					elements.push(formElem);
					break;
				default :
					if (formElem === this.liveFormField) {
						elements.push(formElem);
					}
			}
		}
	}

	for (i = 0; i < elements.length; i++) {
		formElem = elements[i];
		switch (formElem.type) {
			// text, select, hidden, password, textarea elements
			case 'text':
			case 'select-one':
			case 'hidden':
			case 'password':
			case 'textarea':
				strSubmit += formElem.name + '=' + encodeURIComponent(formElem.value) + '&';
				break;
			case 'radio':
			case 'checkbox':
				if (formElem.checked) {
					strSubmit += formElem.name + '=' + encodeURIComponent(formElem.value) + '&';
				}
				break;
			case 'select-multiple':
				var options = formElem.getElementsByTagName("OPTION"), option;
				var j;
				for (j = 0 ; j < options.length ; j++) {
					option = options[j];
					if (option.selected) {
						strSubmit += formElem.name + '=' + encodeURIComponent(option.value) + '&';
					}
				}
				break;
			case 'file':
				if (formElem.value) {
					hasFile = true;
				}
				break;
		}
	}
	return {'query' : strSubmit, 'hasFile' : hasFile};
};

FormManager.prototype.loadResponse = function(req) {
	var scripts;
	if (req.getResponseHeader('Content-Type').indexOf('text/xml') !== -1) {
		switch(req.responseXML.documentElement.nodeName) {
			case 'fragments' :
				if (this.hasFile) {
					var sb = this.submitButton;
					if (sb) {
						var h = document.createElement('input');
						h.type = 'hidden';
						h.name = sb.name;
						h.value = sb.value;
						this.form.appendChild(h);
					}
					
					this.form.submit();
					return;
				}
				var fragments = req.responseXML.documentElement.childNodes;
				var element, dest, i, j;
				for (i=0 ; i < fragments.length ; i++) {
					element = fragments[i];
					switch (element.nodeName) {
						case 'fragment' :
							dest = document.getElementById(element.getAttribute('id'));
							if(dest) {
								dest.innerHTML = element.firstChild.nodeValue;
								scripts = dest.getElementsByTagName('script');
								for (j=0 ; j < scripts.length ; j++) {
									globalScriptRegistry.loadScript(scripts[j]); }
							}
							break;
						case 'base' :
							var headBase = document.getElementsByTagName('base');
							if (headBase.length > 0) {
								headBase[0].setAttribute('href', element.getAttribute('href'));
							}
							else {
								headBase = document.createElement('base');
								headBase.setAttribute('href', element.getAttribute('href'));
								document.head.appendChild(headBase);
							}
							break;
					}
				}
				break;
			case 'error':
				alert(req.responseXML.documentElement.firstChild.nodeValue);
				return;
		}
	}
	else {
		this.responseTextDest.innerHTML = req.responseText;
		scripts = this.responseTextDest.getElementsByTagName('script');
		var k;
		for (k=0 ; k < scripts.length ; k++) {
			globalScriptRegistry.loadScript(scripts[k]);
		}
	}
	
	var onAfterPopulate = this.onAfterPopulate;
	onAfterPopulate();
	this.scrollToPortalMessage();
	var url = this.form.action;
	if (!this.noHistory){ history.pushState(url, document.title, url); }
};

FormManager.prototype.scrollToPortalMessage = function() {
	var psm = document.getElementById('DesktopStatusBar');
	if (psm) {
		var msgOffset = psm.offsetTop;
		smoothScroll(window.scrollY, msgOffset);
		shake(psm, 10, 1000);
	}
};

FormManager.prototype._fitField = function(evt) {
	var ob = getTargetedObject(evt);
	var inputWidth = ob.value.length / 1.9;
	inputWidth = (inputWidth > 5) ? inputWidth : 5;
	ob.style.width = inputWidth + 'em';
};

function initForms(baseElement, lazy) {
	if (!baseElement) {
		baseElement = document;
	}
	var dest = document.getElementById("mainCell");
	var forms = baseElement.getElementsByTagName("form");
	var f, i;
	for (i = 0 ; i < forms.length ; i++ ) {
		f = new FormManager(forms[i], dest, lazy);
	}
}

function smoothScroll(from, to) {
	var intervalId;
	var step = 25;
	var pos = from;
	var dir;
	if (to > from) {
		dir = 1;
	}
	else {
		dir = -1;
	}

	var jump = function() {
		window.scroll(0, pos);
		pos = pos + step * dir;
		if ((dir === 1 && pos >= to) ||
			(dir === -1 && pos <= to)) {
			window.clearInterval(intervalId);
			window.scroll(0, to);
		}
	};
	intervalId = window.setInterval(jump, 10);
}

/* adapted from http://xahlee.info/js/js_shake_box.html */
function shake(e, distance, time) {
	// Handle arguments
	if (!time) { time = 500; }
	if (!distance) { distance = 5; }

	// Save the original style of e, Make e relatively positioned, Note the animation start time, Start the animation
	var originalStyle = e.style.cssText;
	e.style.position = "relative";
	var start = (new Date()).getTime();

	// This function checks the elapsed time and updates the position of e.
	// If the animation is complete, it restores e to its original state.
	// Otherwise, it updates e's position and schedules itself to run again.
	function animate() {
		var now = (new Date()).getTime();
		// Get current time
		var elapsed = now-start;
		// How long since we started
		var fraction = elapsed/time;
		// What fraction of total time?
		if (fraction < 1) {
			// If the animation is not yet complete
			// Compute the x position of e as a function of animation
			// completion fraction. We use a sinusoidal function, and multiply
			// the completion fraction by 4pi, so that it shakes back and
			// forth twice.
			var x = distance * Math.sin(fraction*8*Math.PI);
			e.style.left = x + "px";
			// Try to run again in 25ms or at the end of the total time.
			// We're aiming for a smooth 40 frames/second animation.
			setTimeout(animate, Math.min(25, time-elapsed));
		}
		else {
			// Otherwise, the animation is complete
			e.style.cssText = originalStyle; // Restore the original style
		}
	}
	animate();
}

}());
