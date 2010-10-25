// © Benoît PIN 2006-2009
// http://plinn.org
// Licence GPL
// $Id: root_handlers.js 1467 2009-02-10 13:25:38Z pin $
// $URL: http://svn.cri.ensmp.fr/svn/Plinn/branches/CMF-2.1/skins/ajax_scripts/root_handlers.js $

/* Ajax for everything : if an click event has not been intercepted before */

var AjaxLinkHandler;

(function(){

var reProtocol = /^\s*[a-z]+:/;

AjaxLinkHandler = function(locationPollInterval) {
	var thisHandler = this;
	this.previousHash = '#' + location.href;
	location.hash = location.href;
	setInterval(function(){thisHandler.checkLocation();}, locationPollInterval)
	addListener(document.body, 'click', function(evt){thisHandler.handleClick(evt);});
	if (browser.isIE55 || browser.isIE6up) {
		var ie_historyFrm = document.createElement('iframe');
		ie_historyFrm.setAttribute('src', portal_url() + '/scrape_ie_history');
		with (ie_historyFrm.style) {
			border="0";
			width="1px";
			height="1px";
			position="absolute";
			bottom="0";
			right="0";
			visibility="visible";
		}
		document.body.appendChild(ie_historyFrm);
		this.historyFrame = ie_historyFrm;
	}
};

AjaxLinkHandler.prototype.checkLocation = function() {
	if ((this.previousHash != location.hash) && location.hash) {
		var rawUrl = unescape(location.hash.slice(1));
		
		var urlHash = rawUrl.split('#');
		var url = urlHash[0];
		var hash = urlHash[1];
		
		var ajaxParams='ajax=1&_browserObjectUrl=' + escape(absolute_url());
		var urlQueryStart = url.indexOf('?');
		if (urlQueryStart != -1)
			url += '&' + ajaxParams;
		else
			url += '?' + ajaxParams;

		try {
			var fi = new FragmentImporter(url);
			if (hash) {
				var thisHandler = this;
				fi.onAfterPopulate = function(){thisHandler.loadHash('#' + hash);};
			}
			fi.load(rawUrl);
		}
		catch (e) {
			window.location.href = rawUrl;
		}
	}
	this.previousHash = location.hash;
};

AjaxLinkHandler.prototype.handleClick = function(evt){
	var target = getTargetedObject(evt);
	while (target.nodeName != 'A') {
		target = target.parentNode;
		if (target == document.body)
			return;
	}
	target.blur();
	// prevent click glitches from IE :((
	if (browser.isIE55 || browser.isIE6up) {
		if (_disableRootClickHandler)
			return;
		else {
			_disableRootClickHandler = true;
			setTimeout("_disableRootClickHandler=false", 100);
		}
	}
	
	if (target.target)
		return;
		
	var url;
	var m = reProtocol.exec(target.getAttribute('href', 2));
	if (m) {
		var protocol = m[0];
		if (protocol == location.protocol)
			url = target.href;
		else
			return;
	}
	else
		url = absolute_url() + '/' + target.getAttribute('href', 2);
	
	if (!url) return;
	
	if (browser.isGecko)
		url = encodeURIComponent(url);
	var query = target.search;
	if ((query && query.search("noajax=1") != -1) || target.name == 'noajax')
		return;
	
	disableDefault(evt);
	this.loadUrl(url);
};

if (browser.isIE55 || browser.isIE6up) {
	AjaxLinkHandler.prototype.loadUrl = function(url) {
		if (location.hash.slice(1) == url)
			url += '#'
		this.historyFrame.contentWindow.location.search = '?url=' + escape(url);
		location.hash = escape(url);
	};
}
else {
	AjaxLinkHandler.prototype.loadUrl = function(url) {
		if (location.hash.slice(1) == url)
			url += '#'
		location.hash = escape(url);
	};	
}

AjaxLinkHandler.prototype.loadHash = function(hash) {
	this.previousHash = hash;
	location.hash = hash;
};

AjaxLinkHandler.prototype.ie_loadHistory = function(url) {
	location.hash = escape(url);
};

function ajaxSubmitFormHandler(evt) {
	var target = getTargetedObject(evt);
	if (target.nodeName == 'INPUT' && (target.type == 'submit' || target.type == 'image')) {
		var form = target;
		while (form != document) {
			form = form.parentNode;
			if (form.nodeName == 'FORM') {
				var fm = new FormManager(form, document.getElementById("mainCell"));
				fm.submitButton = target;
				//disableDefault(evt);
				break;
			}
		}
	}
	
}

function _addRootHandlers() {
	if ((AJAX_CONFIG & 1) == 1) {
		window.linkHandler = new AjaxLinkHandler(200);
	    if (browser.isIE55 || browser.isIE6up) {
	    	_disableRootClickHandler = false;
	    }
	}
	if ((AJAX_CONFIG & 2) == 2) {
		addListener(document, 'click', ajaxSubmitFormHandler);
	}
}

registerStartupFunction(_addRootHandlers);

})();