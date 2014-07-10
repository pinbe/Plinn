// (c) Benoît PIN 2006-2014
// http://plinn.org
// Licence GPL
// 
// 
// Meta functions for events management.

var addListener; /* (ob, eventName, listenerFunction, group) add event listener eventName without "on" prefix.
				 *	optionally, listeners can be grouped to make removing convenient.
				 */
var removeListener; // (ob, eventName, listenerFunction, group) remove event listener.
var removeGroupListeners; // (group) remove all listeners in group.
var raiseMouseEvent; // (ob, eventName) raise mouse event (without "on" prefix) on object.

var getTargetedObject; // (event) retrieves the object that fired the event. Event parameter is optional.
var getEventObject; // (event) return the event object. Event parameter is optional.
var disableDefault; // (event) disable default event's action. Event parameter is optional.
var disablePropagation; // (event) disable event propagation or bubbling.

// etc utils
var getWindowWidth; // returns browser's window width
var getWindowHeight; // returns browser's window height
var clearSelection; // clear current selection (useful on drag and drop)
var getCopyOfNode; /* (node) returns a clone of the given node.
					* Useful when :
						* the node came from a foreign document (eg. XmlHttpRequest xml reponse)
						* to inject HMTL code inside tags where innerHtml is read only (IE)
					*/

var copyPrototype; // (descendant, parent) lightwheight javascript inheritance
if (!history.pushState) {
	history.pushState = function(){};
}

(function(){

function buildMetaFunctions() {
	addListener = _build_addListener();
	removeListener = _build_removeListener();
	raiseMouseEvent = _build_raiseMouseEvent();

	getTargetedObject = _build_getTargetedObject();
	getEventObject = _build_getEventObject();
	disableDefault = _build_disableDefault();
	disablePropagation = _build_disablePropagation();
	getWindowWidth = _build_getWindowWidth();
	getWindowHeight = _build_getWindowHeight();
	getWindowScrollX = _build_getWindowScrollX();
	getWindowScrollY = _build_getWindowScrollY();
	clearSelection = _build_clearSelection();
}

var __groupListeners = {};

function _build_addListener() {
	var _browserSpecific;
	if (!browser.isDOM2Event) {
		_browserSpecific = function(ob, eventName, listenerFunction) {
			eventName = "on" + eventName;
			ob.attachEvent(eventName, listenerFunction);
		};
	}
	else {
		_browserSpecific = function(ob, eventName, listenerFunction) {
			ob.addEventListener(eventName, listenerFunction, false); // only bubbling events :-(
		};
	}
	var common = function(ob, eventName, listenerFunction, group) {
		_browserSpecific(ob, eventName, listenerFunction);
		if (group) {
			if(!__groupListeners[group]) {
				__groupListeners[group] = [];}
			__groupListeners[group].push([ob, eventName, listenerFunction]);
		}
	};
	return common;
}

function _build_removeListener() {
	if (!browser.isDOM2Event) {
		var _ie_removeListener = function(ob, eventName, listenerFunction) {
			eventName = "on" + eventName;
			ob.detachEvent(eventName, listenerFunction);
		};
		return _ie_removeListener;
	}
	else {
		var _dom2_removeListener = function(ob, eventName, listenerFunction) {
			ob.removeEventListener(eventName, listenerFunction, false); // only bubbling events :-(
		};
		return _dom2_removeListener;
	}
}

removeGroupListeners = function(group) {
	var listeners = __groupListeners[group];
	var l, i;
	for (i=0 ; i<listeners.length ; i++){
		l = listeners[i];
		removeListener(l[0], l[1], l[2]);
	}
	__groupListeners[group] = null;
		
};

function  _build_raiseMouseEvent() {
	if (!browser.isDOM2Event) {
		var _ie_raiseMouseEvent = function(ob, eventName) {
			ob.fireEvent("on" + eventName);
		};
		return _ie_raiseMouseEvent;
	}
	else {
		var _dom2_raiseMouseEvent = function(ob, eventName) {
			var event = document.createEvent("MouseEvents");
			event.initEvent(eventName, true, true);
			ob.dispatchEvent(event);
		};
		return _dom2_raiseMouseEvent;
	}
}

function _build_getTargetedObject(){
	if (!browser.isDOM2Event) {
		var _ie_getTargetedObject = function() {
			return window.event.srcElement;
		};
		return _ie_getTargetedObject;
	}
	else {
		var _appleWebKit_getTargetedeObject = function(evt) {
			var target = evt.target;
			// is it really safe ?...
			return (target.nodeType === 3) ? target.parentNode : target;
		};
		var _dom2_getTargetedObject = function(evt) {
			return evt.target;
		};
		return (browser.isAppleWebKit) ? _appleWebKit_getTargetedeObject : _dom2_getTargetedObject;
	}
}

function _build_getEventObject(){
	if (!browser.isDOM2Event) {
		var _ie_getEventObject = function() {
			return window.event;
		};
		return _ie_getEventObject;
	}
	else {
		var _dom2_getEventObject = function(evt) {
			return evt;
		};
		return _dom2_getEventObject;
	}
}


function _build_disableDefault(){
	if (!browser.isDOM2Event) {
		var _ie_disableDefault = function() {
			window.event.returnValue = false;
		};
		return _ie_disableDefault;
	}
	else {
		var _dom2_disableDefault = function(evt) {
			evt.preventDefault();
		};
		return _dom2_disableDefault;
	}
}

function _build_disablePropagation() {
	if (!browser.isDOM2Event) {
		var _ie_disablePropagation = function() {
			window.event.cancelBubble = true;
		};
		return _ie_disablePropagation;
	}
	else {
		var _dom2_disablePropagation = function(evt) {
			evt.stopPropagation();
		};
		return _dom2_disablePropagation;
	}
}

function _build_getWindowWidth() {
	if (window.innerWidth !== undefined){
		return function(){
			return window.innerWidth;
			};
	}
	else {
		return function(){
			return document.documentElement.clientWidth;
		};
	}
}

function _build_getWindowHeight() {
	if (window.innerHeight !== undefined) {
		return function(){
			return window.innerHeight;
		};
	}
	else {
		return function(){
			return document.documentElement.clientHeight;
		};
	}
}

function _build_getWindowScrollX() {
	if (window.scrollX !== undefined) {
		return function(){
			return window.scrollX;
		};
	}
	else {
		return function(){
			return document.body.scrollLeft;
		};
	}
}

function _build_getWindowScrollY() {
	if (window.scrollY !== undefined) {
		return function(){
			return window.scrollY;
		};
	}
	else {
		return function(){
			return document.body.scrollTop;
		};
	}
}

function _build_clearSelection() {
	if (document.selection) {
		return function() {
			document.selection.clear();
		};
	}
	else {
		return function() {
			window.getSelection().removeAllRanges();
		};
	}
}

buildMetaFunctions();

addListener(window, 'load', function(evt) {
	// html5 facade
	if (!document.body.classList) {
		var nop = function(){};
		var fakeDOMTokenList = {'length':0, 'item':nop, 'contains':nop, 'add':nop, 'remove':nop, 'toggle':nop};
		Element.prototype.classList = fakeDOMTokenList;
	}
});



var ELEMENT_NODE = 1;
var TEXT_NODE = 3;
var _setAttribute;
getCopyOfNode = function(node) {
	
	switch(node.nodeType) {
		case ELEMENT_NODE:
			var attributes = node.attributes;
			var childs = node.childNodes;
	
			var e = document.createElement(node.nodeName);

			var attribute, i;
			for(i=0 ; i<attributes.length ; i++) {
				attribute = attributes[i];
				_setAttribute(e, attribute.name, attribute.value);
			}
			
			for(i=0 ; i<childs.length ; i++) {
				e.appendChild(getCopyOfNode(childs[i]));}
			
			return e;

		case TEXT_NODE:
			return document.createTextNode(node.nodeValue);
	}
};

if (browser.isIE) {
	_setAttribute = function(e, name, value) {
		// workarround IE lack of dom implementation.
		switch(name.toLowerCase()) {
			case 'colspan' :
				e.colSpan = value;
				break;
			case 'class' :
				e.className = value;
				break;
			case 'style' :
				loadCssText(e, value);
				break;
			default:
				if (name.slice(0,2) === 'on') { // event handler
					// A browser normaly eval text code attached to a onXyz attribute. Not IE.
					/*jslint evil: true */
					e[name] = function(){eval(value);};}
				else {
					e.setAttribute(name, value);}
		}
	};
	var reCompoundPropName = /^\s*([^\-]+)\-([a-z])([a-z]+)\s*$/;
	var _capitalizeCssPropName = function (s, g1, g2, g3) { // gN args match above regexp groups 
		if(g2) {
			return g1 + g2.toUpperCase() + g3;}
		else {
			return s;}
	};

	var loadCssText = function (e, cssText) {
		var pairs = cssText.split(';');
		var pair, name, value, i;
		var style = e.style;
		for (i= 0; i < pairs.length; i++) {
			pair = pairs[i].split(':');
			if (pair.length === 2) {
				name = _capitalizeCssPropName(pair[0]);
				value = pair[1];
				style[name] = value;
			}
		}
	};
}
else {
	_setAttribute = function(e, name, value) {e.setAttribute(name, value);};
}

/* 
* http://www.sitepoint.com/blogs/2006/01/17/javascript-inheritance/
*/

copyPrototype = function (descendant, parent) { 
	var sConstructor = parent.toString(); 
	var aMatch = sConstructor.match( /\s*function (.*)\(/ );
	if ( aMatch !== null ) { descendant.prototype[aMatch[1]] = parent; }
	var m;
	for (m in parent.prototype) {
		if (parent.prototype.hasOwnProperty(m)) {
			descendant.prototype[m] = parent.prototype[m]; }
	}
};

}());
