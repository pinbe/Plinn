// © 2009 Benoît Pin
// http://plinn.org
// Licence GPL
// $Id: widget_form_manager.js 1535 2009-10-21 16:56:13Z pin $
// $URL: http://svn.cri.ensmp.fr/svn/Plinn/branches/CMF-2.1/skins/ajax_scripts/widget_form_manager.js $

var WidgetBasedFormManager;

(function(){
	WidgetBasedFormManager = function(widgets, editingArea, dataArea, dataAreaSpecs, afterShow) {
		/* widgets : {'add':element, 'edit':element} element targets nodes to clone.
		*  editingArea : surrounding element where form is
		*  dataArea : element where data are
		*  dataAreaSpecs : by default, param used to indicate the total number of columns
		*  afterShow : function called after a widget insertion
		*/
		var thisWgtManager = this;
		this.widgets = widgets;
		this.openedWidget = null;
		this.dataArea = dataArea;
		this.dataAreaSpecs = dataAreaSpecs;
		this.afterShow = afterShow;

		var form = editingArea.getElementsByTagName('form')[0];
		this.form = form;
		var fm = new FormManager(form);
		fm.onBeforeSubmit  = function(fm, evt){return thisWgtManager.onBeforeSubmit(fm, evt);};
		fm.onResponseLoad = function(req){thisWgtManager.loadResponse(req);};
		
		addListener(this.form, 'click', function(evt){thisWgtManager.clickHandler(evt);});
		
	};
		
	WidgetBasedFormManager.prototype.showAddWidget = function(dest) {
		if (this.openedWidget)
			return;
		var wdgtCopy = this.widgets['add'].cloneNode(true);
		wdgtCopy.removeAttribute('id');
		this.openedWidget = wdgtCopy;
		dest.appendChild(wdgtCopy);
		if (this.addButton)
			this.addButton.style.visibility = 'hidden';
		if (this.afterShow)
			this.afterShow(this);
	};
	
	WidgetBasedFormManager.prototype.showPopulatedWidget = function(dest, url) {
		var req = new XMLHttpRequest();
		req.open("GET", url, false);
		showProgressImage();
		req.send(null);
		hideProgressImage();
		
		if (req.status != 200){
			alert(req.status);
			return;
		}

		var wdgtCopy = this.widgets['edit'].cloneNode(true);
		wdgtCopy.removeAttribute('id');
		var tmpForm = document.createElement('form');
		tmpForm.appendChild(wdgtCopy);
		
		var fields = req.responseXML.documentElement.childNodes;
		var input, field, value;
		for (var i = 0 ; i<fields.length; i++) {
			field = fields[i];
			if (!field.firstChild)
				continue;
			
			value = field.firstChild.nodeValue;
			input = tmpForm.elements.namedItem(field.nodeName);

			switch (input.tagName) {
				case 'INPUT':
					input.value = value;
					break;
				case 'TEXTAREA':
					input.appendChild(document.createTextNode(value));
			}
		}
		dest.appendChild(wdgtCopy);
		if (this.afterShow)
			this.afterShow(this);
	};
	
	WidgetBasedFormManager.prototype.cancelWidget = function() {
		var parent = this.openedWidget.parentNode;
		parent.removeChild(this.openedWidget);
		this.openedWidget = null;
		if (this.addButton)
			this.addButton.style.visibility = 'visible';
		if (this.previousRecState) {
			this.previousRecState.style.display = '';
			this.previousRecState = null;
		}
	};
	
	WidgetBasedFormManager.prototype.updateEditedRecord = function(node) {
		var parent = this.openedWidget.parentNode;
		parent.removeChild(this.openedWidget);
		this.openedWidget = null;
		if (this.addButton)
			this.addButton.style.visibility = 'visible';
		
		parent = this.previousRecState.parentNode;
		parent.replaceChild(node, this.previousRecState);
	};

	WidgetBasedFormManager.prototype.clickHandler = function(evt) {
		var target = getTargetedObject(evt);
		if (target.tagName == 'IMG') {
			var parent = target.parentNode;
			if (parent.tagName == 'A') {
				switch (parent.name) {
					case 'add' :
						disableDefault(evt);
						disablePropagation(evt);
						parent.blur();
						this.addButton = parent;
						this.showAddWidget(this.form);
						break;
					case 'rm' :
						disableDefault(evt);
						disablePropagation(evt);
						this.deleteRecord(parent);
						break;
					case 'edit' :
						disableDefault(evt);
						disablePropagation(evt);
						if (!this.openedWidget) {
							var rec = this._storePreviousState(parent);
							var container = this._prepareEditingContainer(rec);
							this.showPopulatedWidget(container, parent.href);
						}
						break;
				}
			}
		}
	};
	
	WidgetBasedFormManager.prototype._storePreviousState = function(recChild) {
		var rec = recChild;
		while(!(this.isRootRecordElement(rec)))
			rec = rec.parentNode;
		rec.style.display = 'none';
		this.previousRecState = rec;
		return rec
	};
	
	WidgetBasedFormManager.prototype._prepareEditingContainer = function(rec) {
		/* default behaviour. May be redefined by an instance */
		var tbody = document.createElement('tbody');
		var tr = document.createElement('tr');
		var td = document.createElement('td')
		td.colSpan = this.dataAreaSpecs;

		tbody.appendChild(tr);
		tr.appendChild(td)
		
		if (rec.nextSibling)
			rec.parentNode.insertBefore(tbody, rec.nextSibling);
		else
			rec.parentNode.appendChild(tbody);
		
		this.openedWidget = tbody;
		return td
	};
	
	
	
	WidgetBasedFormManager.prototype.deleteRecord = function(link) {
		var req = new XMLHttpRequest();

		var thisManager = this;
		req.onreadystatechange = function() {
			switch (req.readyState) {
				case 1 :
					showProgressImage();
					break;
				case 4 :
					hideProgressImage();
					if (req.status == 200)
						thisManager._deleteHtmlRecord(req, link);
					else
						alert('Error: ' + req.status);
			};
		};
		var url = link.href;
		req.open("POST", url, true);
		req.send(null);
	};
	
	
	WidgetBasedFormManager.prototype._deleteHtmlRecord = function(req, link) {
		var doc = req.responseXML.documentElement;
		switch (doc.nodeName) {
			case 'done':
				var rec = link.parentNode;
				while(!(this.isRootRecordElement(rec)))
					rec = rec.parentNode;
				this.dataArea.removeChild(rec);
				break;
			case 'error':
				alert(doc.firstChild.nodeValue);
				break;
		}
	};
	
	WidgetBasedFormManager.prototype.isRootRecordElement = function(e) {
		/* default behaviour. May be redefined by an instance */
		return (e.tagName == 'TBODY')
	};
	
	WidgetBasedFormManager.prototype.onBeforeSubmit = function(fm, evt) {
		if (fm.submitButton.name == 'cancel'){
			this.cancelWidget();
			return 'cancelSubmit';
		}
	};
	
	
	WidgetBasedFormManager.prototype.loadResponse = function(req) {
		if (req.status == 200) {
			var doc = req.responseXML.documentElement;
			switch (doc.nodeName) {
				case 'computedField':
					switch(doc.getAttribute('type')) {
						case 'added' :
							this.cancelWidget();
							this.dataArea.appendChild(getCopyOfNode(doc.firstChild));
							break;
					
						case 'edited' :
							this.updateEditedRecord(getCopyOfNode(doc.firstChild));
					}
					break;
				
				case 'error':
					alert(doc.firstChild.nodeValue);
					break;

				case 'fragments' :
					var fragments = req.responseXML.documentElement.childNodes;
					var fragment, dest, scripts;
					for (var i=0 ; i<fragments.length ; i++) {
						fragment = fragments[i];
						if (fragment.nodeName == 'fragment') {
							dest = document.getElementById(fragment.getAttribute('id'));
							dest.innerHTML = fragment.firstChild.nodeValue;

							scripts = dest.getElementsByTagName('script');
							for (var j=0 ; j < scripts.length ; j++)
								globalScriptRegistry.loadScript(scripts[j]);
						}
					}
					break;
			}
		}
		else
			alert(req.statut);
	};
	
})();
