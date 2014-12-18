// © Benoît PIN 2006-2013
// http://plinn.org
// Licence GPL
// 
// 

/* Ajax for everything : if an click event has not been intercepted before */

var AjaxLinkHandler;

(function(){

var reProtocol = /^\s*[a-z]+:/;

AjaxLinkHandler = function() {
	var self = this;
	addListener(document.body, 'click', function(evt){self.handleClick(evt);});
    addListener(window, 'popstate', function(evt){self.handlePopState(evt);});
};

AjaxLinkHandler.prototype.handleClick = function(evt){
	var target = getTargetedObject(evt);
	while (target.nodeName != 'A') {
		target = target.parentNode;
		if (target == document.body)
			return;
	}
	target.blur();

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

    var query = target.search;
    if ((query && query.search("noajax=1") != -1) || target.name == 'noajax')
        return;
    
    disableDefault(evt);
    this.loadUrl(url);
};

AjaxLinkHandler.prototype.handlePopState = function (evt, extra) {
    if (evt.state)
        this.loadUrl(evt.state, true);
};

AjaxLinkHandler.prototype.loadUrl = function(url, noPush) {
    var rawUrl = url;
    var ajaxParams='ajax=1&_browserObjectUrl=' + escape(absolute_url());
	var urlQueryStart = url.indexOf('?');
	if (urlQueryStart != -1)
		url += '&' + ajaxParams;
	else
		url += '?' + ajaxParams;
	
	try {
		var fi = new FragmentImporter(url);
		fi.load();
	}
	catch (e) {
		window.location.href = rawUrl;
		return;
	}
	if (!noPush)
	    history.pushState(rawUrl, '', rawUrl)
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
				break;
			}
		}
	}
}

function _addRootHandlers() {
	if ((AJAX_CONFIG & 1) == 1 && history.pushState !== undefined) {
		window.linkHandler = new AjaxLinkHandler(200);
	}
	if ((AJAX_CONFIG & 2) == 2) {
		addListener(document, 'click', ajaxSubmitFormHandler);
	}
}

registerStartupFunction(_addRootHandlers);

})();