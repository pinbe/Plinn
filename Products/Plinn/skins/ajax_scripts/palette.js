// (c) Benoît PIN 2006
// http://plinn.org
// Licence GPL
// 
// 


function InspectorPalette(baseUrl, toggleButton, contentNode, onExpand, onCollapse) {
	var thisInspector = this;
	this._preloadImages();
	this.baseUrl = baseUrl;
	this.toggleButton = toggleButton;
	this.toggleButton.src = baseUrl + '/collapsedPalette.gif';
	this.contentNode = contentNode;
	this.expanded = false;
	this.onExpand = onExpand ? onExpand : function(){thisInspector.contentNode.innerHTML='expanded';};
	this.onCollapse = onCollapse ? onCollapse : function(){thisInspector.contentNode.innerHTML='collapsed';};
	
	toggleButton.onclick = function(evt) {
		if (thisInspector.expanded)
			thisInspector.collapse();
		else
			thisInspector.expand();
		disableDefault(evt);
		disablePropagation(evt);
		toggleButton.parentNode.blur();
	};
}

InspectorPalette.prototype._preloadImages = function() {
	var images = ['expandPalette.gif', 'collapsePalette.gif', 'expandedPalette.gif', 'collapsedPalette.gif' ], img;
	for (var i=0 ; i<images.lenght ; i++) {
		img = new Image();
		img.src = this.baseUrl + '/' + images[i];
	}
}

InspectorPalette.prototype.expand = function() {
	var toggleButton = this.toggleButton;
	if (toggleButton.blur) toggleButton.blur();
	toggleButton.src = this.baseUrl + '/expandPalette.gif';
	var staticButtonSrc = this.baseUrl + '/expandedPalette.gif';
	window.setTimeout(function(){toggleButton.src = staticButtonSrc;}, 500);
	this.onExpand(this);
	this.expanded = true;
}

InspectorPalette.prototype.collapse = function() {
	var toggleButton = this.toggleButton;
	if (toggleButton.blur) toggleButton.blur();
	toggleButton.src = this.baseUrl + '/collapsePalette.gif';
	var staticButtonSrc = this.baseUrl + '/collapsedPalette.gif';
	window.setTimeout(function(){toggleButton.src = staticButtonSrc;}, 500);
	this.onCollapse(this);
	this.expanded = false;
}