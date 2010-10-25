// © Benoît PIN 2008
// http://plinn.org
// Licence GPL
// $Id: input_completion.js 1409 2008-10-30 16:15:00Z pin $
// $URL: http://svn.cri.ensmp.fr/svn/Plinn/branches/CMF-2.1/skins/ajax_scripts/input_completion.js $
// Form completion utils

// public names
var TextInputCompletion;

(function(){

UID_ATTEMPT = 8;

TextInputCompletion = function(input, url) {
	this.url = url;
	this.input = input;
	this.previousValue = this.input.value;
	
	var thisManager = this;
	addListener(this.input, 'keyup', function(evt) { thisManager._inputComplete(evt); });
	addListener(this.input, 'blur', function(evt) {thisManager._inputQuit(evt);});
	this.input.cancelNextSubmit = true;

	var uid;
	for (var i=0 ; i<UID_ATTEMPT ;i++) {
		uid = Math.random().toString().slice(2);
		uid = 'completions' + uid;
		if (!document.getElementById(uid))
			break;
	}

	var completions = document.createElement('div');
	completions.id = uid;
	completions.style.position = 'relative';
	completions.style.top = getObjectHeight(input) + 'px';
	
	var parent = input.parentNode;
	parent.insertBefore(completions, input);

	this.completions = completions;
	addListener(this.completions, 'click',
				function(evt){thisManager.selectCompletion(getEventObject(evt));}
				);
	this.selectedCompletion = null;
}


TextInputCompletion.prototype._inputComplete = function(evt) {
	var currentValue = this.input.value;
	if (currentValue == this.previousValue)
		this.selectCompletion(getEventObject(evt));
	else {
		var url = this.url + '?value=' + encodeURIComponent(currentValue);
		url = url + '&uid=' + this.completions.id;
		var thisManager = this;
		var fi = new FragmentImporter(url, function(){thisManager.completeIfOneResult() })
		fi.load();
	}
};

TextInputCompletion.prototype._inputQuit = function(evt) {
	if (this.selectedCompletion) {
		try {
			this.copyCompletion(this.selectedCompletion);
		}
		catch(e){}
	}
	this.selectedCompletion = null;
	thisCompleter = this
	setTimeout(function(){thisCompleter.completions.innerHTML='';}, 200);
};

TextInputCompletion.prototype.selectCompletion = function(evt) {
	var res = this.completions.getElementsByTagName('li');
	if (!res) return;
		
	if (evt.type == 'keyup') {
		var newSelection = false;
		switch(evt.keyCode) {
			case 40: // down key
				if (!this.selectedCompletion) {
					this.selectedCompletion = res[0];
					newSelection = true;
				}
				else if (this.selectedCompletion.nextSibling) {
					this.selectedCompletion.className = '';
					this.selectedCompletion = this.selectedCompletion.nextSibling;
					newSelection = true;
				}
				break;
			case 38: // up key
				if (this.selectedCompletion && this.selectedCompletion.previousSibling) {
					this.selectedCompletion.className = '';
					this.selectedCompletion = this.selectedCompletion.previousSibling;
					newSelection = true;
				}
				break;
			case 13: // enter key
				if (this.selectedCompletion) {
					this.copyCompletion(this.selectedCompletion);
					this.completions.innerHTML = '';
					this.input.cancelNextSubmit = true;
					return;
				}
				break
		}
		if (newSelection) {
			this.selectedCompletion.className = 'selected';
			this.copyCompletion(this.selectedCompletion);
		}
	}
	else if (evt.type=='click') {
		this.selectedCompletion = getTargetedObject(evt);
		this.copyCompletion(this.selectedCompletion);
	}
}

TextInputCompletion.prototype.copyCompletion = function(completion) {
	this.input.value = this.previousValue = completion.firstChild.nodeValue;
}

TextInputCompletion.prototype.completeIfOneResult = function() {
	this.selectedCompletion = null;
	var currentValue = this.input.value;
	
	if (this.previousValue.length < currentValue.length) {
		var res = this.completions.getElementsByTagName('li');
		if (res.length == 1) {
			var completion = res[0];
			this.copyCompletion(completion);
			this.completions.innerHTML = '';
		}
	}
	
	this.previousValue = currentValue;
};

})();