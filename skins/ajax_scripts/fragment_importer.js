// (c) Benoît PIN 2006-2007
// http://plinn.org
// Licence GPL
// 
// 

var FragmentImporter;

(function(){

var isTextMime = /^text\/.+/i;

FragmentImporter = function(url, onAfterPopulate) {
	var thisImporter = this;
	this.url = url;
	this.onAfterPopulate = (!onAfterPopulate) ? function(){return;} : onAfterPopulate;
};

FragmentImporter.prototype._load = function(url) {
	var req = new XMLHttpRequest();
	var thisImporter = this;
	req.onreadystatechange = function() {
		switch (req.readyState) {
			case 1 :
				showProgressImage();
				break;
			case 2 :
				try {
					if (! isTextMime.exec(req.getResponseHeader('Content-Type'))) {
						req.onreadystatechange = null;
						req.abort();
						hideProgressImage();
						window.location.href = thisImporter._fallBackUrl;
					}
				}
				catch(e){}
				break;
			case 4 :
				hideProgressImage();
				if (req.status === 200) {
					thisImporter.populateBaseElement(req); }
				else {
					alert('Error: ' + req.status); }
				break;
		}
	};

	req.open("GET", url, true);
	req.send(null);
};

FragmentImporter.prototype.load = function(fallBackUrl) {
	if (fallBackUrl) {
		this._fallBackUrl = fallBackUrl; }
	else {
		this._fallBackUrl = this.url; }
	this._load(this.url);
};

FragmentImporter.prototype.useMacro = function(template, macro, fragmentId, queryString) {
	var url = this.url + "/use_macro?template=" + template + "&macro=" + macro + "&fragmentId=" + fragmentId;
	if (queryString) {
		url += '&' + queryString; }
	this._load(url);
};


FragmentImporter.prototype.populateBaseElement = function(req) {
	// :( IE : innerHTML is read-only for these tags:
	// COL, COLGROUP, FRAMESET, HTML, STYLE, TABLE, TBODY, TFOOT, THEAD, TITLE, TR
	var contentType = req.getResponseHeader('Content-Type');
	if (! isTextMime.exec(contentType)) {
		window.location.href = this._fallBackUrl;
		return;
	}
	if (contentType.indexOf('text/xml') !== -1) {
		var fragments = req.responseXML.documentElement.childNodes;
		var fragment, dest, scripts, i, j;
		for (i=0 ; i < fragments.length ; i++) {
			fragment = fragments[i];
			if (fragment.nodeName === 'fragment') {
				dest = document.getElementById(fragment.getAttribute('id'));
				if(dest) {
					dest.innerHTML = fragment.firstChild.nodeValue;
					scripts = dest.getElementsByTagName('script');
					for (j=0 ; j < scripts.length ; j++) {
						globalScriptRegistry.loadScript(scripts[j]); }
				}
			}
		}
	}
	this.onAfterPopulate();
};

}());