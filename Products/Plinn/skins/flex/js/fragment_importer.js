// (c) Benoît PIN 2006-2007
// http://plinn.org
// Licence GPL
// 
// 

var FragmentImporter;

(function() {

    var isTextMime = /^text\/.+/i;

    FragmentImporter = function(url, onAfterPopulate) {
        this.url = url;
        this.onAfterPopulate = (!onAfterPopulate) ? function() {
        } : onAfterPopulate;
    };

    FragmentImporter.prototype._load = function(url) {
        var req = new XMLHttpRequest();
        var self = this;
        req.onreadystatechange = function() {
            switch(req.readyState) {
                case 1 :
                    // showProgressImage();
                    break;
                case 2 :
                    try {
                        if(!isTextMime.exec(req.getResponseHeader('Content-Type'))) {
                            req.onreadystatechange = null;
                            req.abort();
                            // hideProgressImage();
                            window.location.href = self._fallBackUrl;
                        }
                    }
                    catch (e) {
                    }
                    break;
                case 4 :
                    // hideProgressImage();
                    if(req.status === 200) {
                        self.populateBaseElement(req);
                    }
                    else {
                        alert('Error: ' + req.status);
                    }
                    break;
            }
        };

        req.open("GET", url, true);
        req.send(null);
    };

    FragmentImporter.prototype.load = function(fallBackUrl) {
        if(fallBackUrl) {
            this._fallBackUrl = fallBackUrl;
        }
        else {
            this._fallBackUrl = this.url;
        }
        this._load(this.url);
    };

    FragmentImporter.prototype.useMacro = function(template, macro, fragmentSelector, queryString) {
        var url = this.url +
                  "/use_macro?template=" + encodeURIComponent(template) +
                  "&macro=" + encodeURIComponent(macro) +
                  "&fragmentSelector=" + encodeURIComponent(fragmentSelector);
        if(queryString) {
            url += '&' + queryString;
        }
        this._load(url);
    };

    FragmentImporter.prototype.populateBaseElement = function(req) {
        var contentType = req.getResponseHeader('Content-Type');
        if(!isTextMime.exec(contentType)) {
            window.location.href = this._fallBackUrl;
            return;
        }

        if(contentType.indexOf('text/xml') !== -1) {
            var fragments = req.responseXML.documentElement.childNodes;
            var element, dest, scripts, i, j;
            for(i = 0; i < fragments.length; i++) {
                element = fragments[i];
                switch(element.nodeName) {
                    case 'fragment' :
                        // dest = document.getElementById(element.getAttribute('id'));
                        dest = document.querySelector(element.getAttribute('selector'));
                        if(dest) {
                            dest.innerHTML = element.firstChild.nodeValue;
                            scripts = dest.getElementsByTagName('script');
                            for(j = 0; j < scripts.length; j++) {
                                globalScriptRegistry.loadScript(scripts[j]);
                            }
                        }
                        break;
                    case 'base' :
                        var headBase = document.getElementsByTagName('base');
                        if(headBase.length > 0) {
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
        }
        this.onAfterPopulate();
    };
}());