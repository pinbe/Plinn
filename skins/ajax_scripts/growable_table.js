// © Benoît PIN 2006-2008
// http://plinn.org
// Licence GPL
// 
// 
// GrowableTable: functions to edit quickly table form entries.

function GrowableTable(tbody, fieldsDescription, submitExtName, skipFormManagerInit) {
	this.fieldsDescription = fieldsDescription;
	this.tbody = tbody;
	this.length = tbody.getElementsByTagName('tr').length;
	this.submitExtName = submitExtName;

	var form = this.tbody.parentNode;
	while (form.tagName != 'FORM') 
		form = form.parentNode;

	var thisManager = this;

	if (!skipFormManagerInit) {
		var formManager = new FormManager(form);
		formManager.onBeforeSubmit = function(m, e){return thisManager.onBeforeSubmit(m, e)};
		formManager.onResponseLoad = function(req){thisManager.loadResponse(req);};
	}
	
	addListener(this.tbody.parentNode, 'click', function(evt){thisManager.tbodyClick(evt);});
	
	var addButton;
	var links = tbody.parentNode.getElementsByTagName('a');
	for (var i=0 ; i<links.length ; i++) {
		addButton = links[i];
		if (addButton.name == 'addrow')
			break;
	}
	this.addButton = addButton;
	this.submittedRow = null;
	this.editedRowInitialValues = null;
	
	
}

GrowableTable.prototype.tbodyClick = function(evt) {
	var ob = getTargetedObject(evt);
	if (ob.tagName == 'IMG') {
		disablePropagation(evt);
		disableDefault(evt);
		
		var link = ob.parentNode;
		var name = link.getAttribute('name');
		
		if (name == 'addrow')
				this.addRow();
		else if (name)
			this.removeRow(ob, name);
	}
	else {
		while (ob.tagName != 'TBODY') {
			if (ob.tagName == 'SPAN')
				break;
			else
				ob = ob.parentNode;
		}
		
		if (ob.tagName == 'SPAN') {
			disablePropagation(evt);
			disableDefault(evt);
			this.replaceRowByFields(ob);
		}
	}
};

GrowableTable.prototype.replaceRowByFields = function(ob) {
	if (this.editedRowInitialValues)
		return;
	this.addButton.className = 'hidden';
	var tr = ob;
	while (tr.tagName != 'TR')
		tr = tr.parentNode;
			
	var span, cell, input, elementName, text;
	var cells = tr.getElementsByTagName('td');
	elementName = cells[0].getElementsByTagName('a')[0].getAttribute('name');
	
	this.editedRowInitialValues = new Array();

	for (var i=1; i < cells.length ; i++) {
		cell = cells[i];
		span = cell.getElementsByTagName('span')[0];
		this.editedRowInitialValues[i-1] = span.innerHTML;
		
		if (span.firstChild && span.firstChild.className == 'hidden_value')
		    text = span.firstChild.innerHTML;
		else
		    text = span.innerHTML;
		
		input = document.createElement('input');
		with(input) {
			type='text';
			name=this.fieldsDescription[i-1][0];
			size=this.fieldsDescription[i-1][1];
			value=text;
		}
		cell.replaceChild(input, span);
		
		if (i == cells.length - 1) {
			var hiddenNameInput = document.createElement('input');
			with (hiddenNameInput){
				type='hidden';
				name='row_edit' + this.submitExtName;
				value=elementName;
			}
			
			var validButton = document.createElement('input');
			with (validButton) {type = 'image'; name = 'row_edit_valid'; src = portal_url() + '/validate.gif'; alt = 'Validate'; height='16'; width='16'}

			var cancelButton = document.createElement('input');
			with (cancelButton) {type = 'image'; name = 'row_edit_cancel'; src = portal_url() + '/cancel.gif'; alt = 'Cancel';}
			
			cell.appendChild(hiddenNameInput)
			cell.appendChild(validButton);
			cell.appendChild(cancelButton);
		}
	}
	return tr;
};

GrowableTable.prototype.cancelEditRow = function(ob) {
	var tr = ob;
	while(tr.tagName != 'TR')
		tr = tr.parentNode;
	
	var cells = tr.getElementsByTagName('td');
	var td, span, text;
	for (var i=1 ; i < cells.length ; i++) {
		td = cells[i];
		while (td.firstChild)
			td.removeChild(td.firstChild);

		span = document.createElement('span');
		td.appendChild(span);
		span.innerHTML = this.editedRowInitialValues[i-1];
	}
	
	this.editedRowInitialValues = null;
	this.addButton.className = '';
}

GrowableTable.prototype.onBeforeSubmit = function(m, evt) {
	var target = getTargetedObject(evt);
	var submitElement, form;
	
	switch (target.tagName) {
		case 'INPUT' :
			submitElement = target;
			form = target.form;
			break;
		case 'FORM' :
			submitElement = m.submitButton;
			form = target;
			break;
	}
	
	switch(submitElement.name) {
		case 'row_cancel':
			this.cancelRow(submitElement);
			break;
		case 'row_edit_cancel':
			this.cancelEditRow(submitElement);
			return 'cancelSubmit';
			break;
		default :
			var submittedRow = submitElement;
			while(submittedRow.tagName != 'TR')
				submittedRow = submittedRow.parentNode;
			this.submittedRow = submittedRow;
			return;
			break;
	}
	
	return 'cancelSubmit';
}

GrowableTable.prototype.loadResponse = function(req) {
	var doc = req.responseXML.documentElement;
	switch (doc.nodeName) {
		case 'computedField':
			var copy = getCopyOfNode(doc.firstChild);
			this.tbody.replaceChild(copy, this.submittedRow);
			this.addButton.className = '';
			this.submittedRow = null;
			this.editedRowInitialValues = null;
			break;
		case 'error':
			alert(doc.firstChild.nodeValue);
			break;
	}
}

GrowableTable.prototype.addRow = function(evt) {
	var fieldDescription, input, fieldName, fieldSize;
	var firstField;
	var tr = document.createElement('tr');
	var td = document.createElement('td');
	var hiddenInputAddRowFlag = document.createElement('input');
	with (hiddenInputAddRowFlag){
		type='hidden';
		name='row_add' + this.submitExtName;
		value='add';
	}
	td.appendChild(hiddenInputAddRowFlag);
	tr.appendChild(td);
	
	for (var i=0 ; i < this.fieldsDescription.length ; i++) {
		fieldDescription = this.fieldsDescription[i];
		fieldName = fieldDescription[0];
		fieldSize = fieldDescription[1];
		
		td = document.createElement('td');
		input = document.createElement('input')
		with(input){type='text'; name=fieldName; size=fieldSize; }
		td.appendChild(input);
		tr.appendChild(td);
		if (i == 0)
			firstField = input;
		if (i == this.fieldsDescription.length -1) {
			var validButton = document.createElement('input');
			with (validButton) {type = 'image'; name = 'row_valid'; src = portal_url() + '/validate.gif'; alt = 'Validate'; height='16'; width='16'}

			var cancelButton = document.createElement('input');
			with (cancelButton) {type = 'image'; name = 'row_cancel'; src = portal_url() + '/cancel.gif'; alt = 'Cancel';}
			
			td.appendChild(validButton);
			td.appendChild(cancelButton);
		}
	}
	
	this.tbody.appendChild(tr);
	this.length += 1;
	firstField.focus();
	this.addButton.className = 'hidden';
	return tr;
};

GrowableTable.prototype.removeRow = function(ob, name) {
	var tr = ob;
	while (tr.tagName != 'TR')
		tr = tr.parentNode;
	
	var form = tr;
	while (form.tagName != 'FORM')
		form = form.parentNode;

	var req = new XMLHttpRequest();
	var thisManager = this;
	req.onreadystatechange = function() {
		switch (req.readyState) {
			case 1 :
				showProgressImage();
				break;
			case 4 :
				hideProgressImage();
				if (req.status == '200') {
					if (req.responseXML.documentElement.tagName == 'done')
						thisManager.tbody.removeChild(tr);
						thisManager.onAfterRemove(name);
				}
				else
					alert('Error: ' + req.status);
		}
	};
	
	var url = form.action;
	req.open("POST", url, true);
	req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;charset=utf-8");
	req.send('name=' + name + '&rm=rm');
}

GrowableTable.prototype.onAfterRemove = function(name) { }

GrowableTable.prototype.cancelRow = function(element) {
	/* element must be on the "descendant-or-self" axis of the row to remove */
	while (element.tagName != 'TR')
		element = element.parentNode;
	this.tbody.removeChild(element);
	this.addButton.className= undefined;
}


/* 
* http://www.sitepoint.com/blogs/2006/01/17/javascript-inheritance/
*/

function copyPrototype(descendant, parent) { 
	var sConstructor = parent.toString(); 
	var aMatch = sConstructor.match( /\s*function (.*)\(/ );
	if ( aMatch != null ) { descendant.prototype[aMatch[1]] = parent; } 
	for (var m in parent.prototype) { 
		descendant.prototype[m] = parent.prototype[m]; 
	}
}
