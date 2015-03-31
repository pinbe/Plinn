// (c) Benoît PIN 2006-2015
// http://plinn.org
// Licence GPL
// 
// 

var ScriptRegistry;
var globalScriptRegistry;

(function() {

function ScriptRegistry() {
	this.loadedScripts = {};
	this.pendingScripts = [];
	this.HEAD = document.getElementsByTagName('head')[0];
	this.isLoading = false;
}

ScriptRegistry.prototype.loadScript = function(scriptOb) {
	var scriptUrl;
	if (typeof(scriptOb) == 'string')
		scriptUrl = scriptOb;
	else
		scriptUrl = scriptOb.getAttribute('src');
	
	if (scriptUrl) {
		if (!this.loadedScripts[scriptUrl])
			this.pendingScripts.push(['url', scriptUrl]);
	}
	else {
		this.pendingScripts.push(['code', scriptOb]);
	}
	if(!this.isLoading && this.pendingScripts.length)
		this._loadNextScript();
};

ScriptRegistry.prototype._loadNextScript = function() {
	var firstScript = this.pendingScripts[0];
	
	switch (firstScript[0]) {
		case 'url':
			var script = document.createElement( "script" );
			script.type	= "text/javascript";
			script.src = firstScript[1];
			this.HEAD.appendChild(script);
			this.loadedScripts[script.src] = true;
			this.isLoading = true;
			var thisRegistry = this;
			if (browser.isIE)
				script.onreadystatechange = function(){
					if (script.readyState == 'complete' || script.readyState == 'loaded')
						thisRegistry._removeScriptAfterLoad();
				};
			else
				script.onload = function(){ thisRegistry._removeScriptAfterLoad(); };
			break;
		case 'code' :
			try {
				/* jshint ignore:start */
				eval(firstScript[1].text);
				/* jshint ignore:end */
			}
			catch(e) {
				if (window.console) {
					console.group('Embedded script error');
					console.error(e);
					console.info(firstScript[1]);
					console.groupEnd();
				}
			}
			this._removeScriptAfterLoad();
			break;
	}
};

ScriptRegistry.prototype._removeScriptAfterLoad = function() {
	this.pendingScripts.shift();
	if(this.pendingScripts.length)
		this._loadNextScript();
	else
		this.isLoading = false;
};

globalScriptRegistry = new ScriptRegistry();

}());