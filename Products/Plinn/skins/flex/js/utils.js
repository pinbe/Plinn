var copyPrototype;
var getCopyOfNode;
var readCookie;
var absolute_url;
var portal_url;

(function() {
    copyPrototype = function(descendant, parent) {
        var sConstructor = parent.toString();
        var aMatch = sConstructor.match(/\s*function (.*)\(/);
        if(aMatch !== null) {
            descendant.prototype[aMatch[1]] = parent;
        }
        var m;
        for(m in parent.prototype) {
            if(parent.prototype.hasOwnProperty(m)) {
                descendant.prototype[m] = parent.prototype[m];
            }
        }
    };

    var ELEMENT_NODE = 1;
    var TEXT_NODE = 3;

    getCopyOfNode = function(node) {

        switch(node.nodeType) {
            case ELEMENT_NODE:
                var attributes = node.attributes;
                var childs = node.childNodes;

                var e = document.createElement(node.nodeName);

                var attribute, i;
                for(i = 0; i < attributes.length; i++) {
                    attribute = attributes[i];
                    e.setAttribute(attribute.name, attribute.value);
                }

                for(i = 0; i < childs.length; i++) {
                    e.appendChild(getCopyOfNode(childs[i]));
                }

                return e;

            case TEXT_NODE:
                return document.createTextNode(node.nodeValue);
        }
    };

    absolute_url = function() {
        var e = document.getElementById("Object_URL");
        if(e)
            return e.innerText;
        else {
            e = document.getElementById("BC_Object_URL");
            if(e)
                return e.innerText;
            else
                return document.body.getAttribute('data-absolute_url');
        }
    };

    portal_url = function() {
        return document.body.getAttribute('data-portal_url');
    };

    readCookie = function(name) {
        // from w3schools.com
        var nameEQ = name + "=";
        var ca = document.cookie.split(';');
        var i;
        for(i = 0; i < ca.length; i++) {
            var c = ca[i];
            while(c.charAt(0) === ' ') {
                c = c.substring(1);
            }
            if(c.indexOf(nameEQ) !== -1) {
                return c.substring(nameEQ.length, c.length);
            }
        }
        return null;
    };


}());