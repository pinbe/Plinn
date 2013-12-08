// (c) Benoît PIN 2006-2007
// http://plinn.org
// Licence GPL
// 
// 

var FolderDDropControler;
var DropTarget;
var loadListing;
var DDFolderUploader;

(function(){

function getTargetRow(evt){
	var target = getTargetedObject(evt);
	while (target.nodeName !== "TR") {
		target = target.parentNode; }
	return target;
}

FolderDDropControler = function(listing) {
	this.folderUrl = document.getElementById("FolderUrl").innerHTML;
	this.targetRow = null;
	this.lastOverPosition = null;
	this.prevDirUp = null;
	this.noOver = true;
	this.listing = listing;
	this.checkboxes = undefined;
	this._updateCBIndex();
	var thisControler = this;
	this.listing.onmousedown	= function(evt) {thisControler.drag(evt);};
	this.listing.onmouseover	= function(evt) {thisControler.moveRow(evt);};
	this.listing.onmouseup		= function(evt) {thisControler.drop(evt);};
	addListener(this.listing, 'click', function(evt) {thisControler.disableClickAfterDrop(evt);});
	addListener(this.listing, 'click', function(evt) {thisControler.selectCBRange(evt);});
	
	if (browser.isIE) {
		this.listing.ondragstart = function() { window.event.returnValue = false;};
	}
};

FolderDDropControler.prototype._updateCBIndex = function() {
	var cbs = this.listing.getElementsByTagName('INPUT');
	var index = 0;
	var cb, i;
	this.checkboxes = [];
	for (i=0 ; i < cbs.length ; i++) {
		cb = cbs[i];
		if (cb.type === 'checkbox') {
			cb.position = index++;
			this.checkboxes[cb.position] = cb;
		}
	}
};

FolderDDropControler.prototype.drag =  function(evt){
	var target = getTargetedObject(evt);
	if (target.nodeName === "INPUT") { return true; }
	disableDefault(evt);
	var targetRow = getTargetRow(evt);
	targetRow.style.backgroundColor = base_properties.highLightColor;
	this.listing.style.cursor = "move";
	this.targetRow = targetRow;
	this.lastOverPosition = targetRow.pos;
};

FolderDDropControler.prototype.moveRow =  function(evt){
	var targetRow = this.targetRow;
	if (targetRow !== null) {
		this.noOver = false;
		if (browser.isIE) {document.selection.clear();}
		var overRow = getTargetRow(evt);

		if (overRow.pos === targetRow.pos) {return;}

		if (this.lastOverPosition < overRow.pos) { // move up
			this.listing.insertBefore(targetRow, overRow.nextSibling);
			this.prevDirUp = true;
			this.lastOverPosition = overRow.pos;
		}
		else if (this.lastOverPosition > overRow.pos) { // move down
			this.listing.insertBefore(targetRow, overRow);
			this.prevDirUp = false;
			this.lastOverPosition = overRow.pos;
		}
		else {
			if (this.prevDirUp) {
				this.prevDirUp = false;
				this.listing.insertBefore(targetRow, overRow);
			}
			else {
				this.prevDirUp = true;
				this.listing.insertBefore(targetRow, overRow.nextSibling);
			}
		}
	}
};

FolderDDropControler.prototype.drop =  function(evt){
	var targetRow = this.targetRow;
	if (targetRow !== null) {
		targetRow.style.backgroundColor="";
		this.listing.style.cursor = "";
		var thisControler = this;
		if (this.noOver) {
			setTimeout(function(){thisControler.reset();}, 50);
			return;
		}
		if (this.lastOverPosition !== null) {
			// get new object position.
			var trim = 0;
			if (targetRow.pos < this.lastOverPosition && !this.prevDirUp) {
				trim = -1; }
			else if (targetRow.pos > this.lastOverPosition && this.prevDirUp) {
				trim = 1; }
		
			// construct url
			var object_id = targetRow.getElementsByTagName("INPUT")[0].getAttribute("value");
			var url = this.folderUrl + "/moveObjectIdToPosition";
			var form ="object_id=" + object_id + "&position:int=" +
					   String(this.lastOverPosition - 1 + trim);

			// reinitialize positions
			var rows = this.listing.getElementsByTagName("TR"), row;
			var i;
			for (i = 0 ; i < rows.length ; i++) {
				row = rows[i];
				row.pos = i+1;
				if (i % 2 === 0){
					row.className = "even";}
				else{
					row.className = "odd";}
			}

			// send request				
			var req = new XMLHttpRequest();
			req.open("POST", url, true);
			req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;charset=utf-8");
			req.send(form);
			setTimeout(function(){thisControler.reset();}, 50);
		}
	}
};

FolderDDropControler.prototype.disableClickAfterDrop = function(evt) {
	var target = getTargetedObject(evt);
	if (!this.noOver) {
		disablePropagation(evt);
		disableDefault(evt);
	}
	this.reset();
};

FolderDDropControler.prototype.selectCBRange = function(evt) {
};


FolderDDropControler.prototype.reset = function() {
	this.targetRow = null;
	this.lastOverPosition = null;
	this.prevDirUp = null;
	this.noOver = true;
};



DropTarget = function(node, folderDDControler) {
	this.folderDDControler = folderDDControler;
	this.batchSize = parseInt(document.getElementById("BatchNavigationSize").innerHTML, 10);
	var thisControler = this;
	node.onmouseup = function(evt){thisControler.drop(evt);};
	node.onmouseover = function(evt) {thisControler.highlightTarget(evt);};
	node.onmouseout = function(evt) {
		var target = getTargetedObject(evt);
		if (target.nodeName === "A" && target.className === "dropPageTarget"){
			target.className = "";}
	};
};

DropTarget.prototype.drop = function(evt) {
	var target = getTargetedObject(evt);
	if (target.nodeName === "A" &&
		target.className !== "previous" && 
		target.className !== "next") {
		var pageNumber = parseInt(target.innerHTML, 10);
		var targetRow = this.folderDDControler.targetRow;
		if ( !isNaN(pageNumber) && targetRow) {
			this.folderDDControler.reset();
			var object_id = targetRow.getElementsByTagName("INPUT")[0].getAttribute("value");
			var url = this.folderDDControler.folderUrl + "/moveObjectIdToPosition";
			var form ="object_id=" + object_id + "&position:int=" + String(this.batchSize * (pageNumber-1));
			// send request
			var req = new XMLHttpRequest();
			req.open("POST", url, true);
			req.setRequestHeader("Content-Type", "application/x-www-form-urlencoded;charset=utf-8");
			req.send(form);
			req.onreadystatechange = function() {
				if (req.readyState === 4) {
					switch (req.status) {
						case 200:
						case 204:
						case 1223:
							raiseMouseEvent(target, "click");
							break;
						default:
							alert('Error: ' + req.status);
					}
				}
			};
		}
	}
};

DropTarget.prototype.highlightTarget = function(evt){
	if (browser.isIE) {document.selection.clear();}
	var target = getTargetedObject(evt);
	if (this.folderDDControler.targetRow &&
		target.nodeName === "A" &&
		target.className !== "previous" &&
		target.className !== "next"){
		target.className = "dropPageTarget";}
};




loadListing = function(evt) {
	var target = getTargetedObject(evt);
	disableDefault(evt);
	disablePropagation(evt);
	var url;
	switch (target.nodeName) {
		case "A" :
			var parts = target.href.split('?');
			url = parts[0];
			var query = '';
			if (parts.length === 2){
				query = parts[1];}
			
			var urlParts = url.split("/");
			url = urlParts.slice(0,urlParts.length-1).join("/");
			if (query.search("template") === -1){
				query += "&template=folder_contents_macros&macro=FolderListing&fragmentId=FolderListing";}
			url = url + "/folder_contents?" + query;
			
			var fi = new FragmentImporter(url);
			fi.load();
			break;

		case "IMG" :
			if (target.id === 'SetSortingAsDefault') {
				var parent = target.parentNode;
				url = parent.href;
				url = url.replace("folder_contents", "folder_sort_control");
				parent.parentNode.removeChild(parent);
				
				var req = new XMLHttpRequest();
				req.open("GET", url, true);
				req.send(null);
			}
			break;
	}
	return false;
};

DDFolderUploader = function(dropbox, uploadUrl, listing) {
	DDFileUploaderBase.apply(this, [dropbox, uploadUrl]);
	this.listing = listing;
	this.progressBarMaxSize = listing.clientWidth;
	var thead = listing;
	do {
		thead = thead.previousSibling;
	} while (thead.tagName !== 'THEAD');

	var cells = thead.getElementsByTagName('th');
	var cell, i;
	this.tableSpan = 0;
	for (i=0 ; i < cells.length ; i++) {
		cell = cells[i];
		this.tableSpan += cell.getAttribute('colspan') ? Number(cell.getAttribute('colspan')) : 1;
	}
	var lastRow = listing.lastChild;
	while(lastRow && lastRow.tagName !== 'TR') {
		lastRow = lastRow.previousSibling;
	}
	this.lastRowClassName = lastRow ? lastRow.className : 'even';
};

copyPrototype(DDFolderUploader, DDFileUploaderBase);


DDFolderUploader.prototype.createRow = function(file) {
	var row = document.createElement('tr');
	row.file = file;
	row.className = this.lastRowClassName === 'even' ? 'odd' : 'even';
	this.lastRowClassName = row.className;
	var td = document.createElement('td');
	td.setAttribute('colspan', this.tableSpan);
	var relSpan = document.createElement('span');
	relSpan.style.position = 'relative';
	td.appendChild(relSpan);
	var progressBar = document.createElement('span');
	progressBar.className = 'upload-progress';
	row.progressBar = progressBar;
	relSpan.appendChild(progressBar);
	var fileNameSpan = document.createElement('span');
	fileNameSpan.innerHTML = file.name;
	td.appendChild(fileNameSpan);
	row.appendChild(td);
	this.listing.appendChild(row);
	this.progressBarMaxSize = row.clientWidth;
	return row;
};

// Methods about upload
DDFolderUploader.prototype.handleFiles = function(files) {
	var file, i, row;
	for (i = 0; i < files.length; i++) {
		file = files[i];
		row = this.createRow(file);
		this.uploadQueuePush(row);
	}
};

DDFolderUploader.prototype.beforeUpload = function(item) {
	this.uploadedItem = item;
	this.progressBar = item.progressBar;
};

DDFolderUploader.prototype.uploadCompleteHandlerCB = function(req) {
	var item = this.uploadedItem;
	var row = getCopyOfNode(req.responseXML.documentElement.firstChild);
	row.className = item.className;

	if (req.status === 200) {
		// update
		console.log('todo');
	}
	else if(req.status === 201) {
		// creation
		this.listing.replaceChild(row, item);
		this.progressBarMaxSize = row.clientWidth;
	}
};

DDFolderUploader.prototype.progressHandlerCB = function(progress) {
	// 0 <= progress <= 1
	var size = this.progressBarMaxSize * progress;
	size = Math.round(size);
	this.progressBar.style.width = size + 'px';
};

}());