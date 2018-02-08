// (c) Benoît PIN 2006-2007
// http://plinn.org
// Licence GPL

function openMemberPopup(member_id) {
	var slot = document.getElementById("MemberFormSlot");
	var url = portal_url() + "/use_macro?template=gruf_macros&macro=member_properties_form&fragmentSelector=%23MemberFormSlot&member_id=" + member_id;
	new FragmentImporter(url, function() {initForms(slot);}).load();
}

function openMemberTreeView(evt) {
	disableDefault(evt);
	disablePropagation(evt);
	var link = getTargetedObject(evt);
	var slot = document.getElementById("MemberFormSlot");
	var member_id = link.href.split("member_id=")[1];
	/* member_id parameter is not necesary at the last position.*/
	var member_id = member_id.split("&");
	var url = portal_url() + "/use_macro?template=gruf_macros&macro=member_tree_view&fragmentSelector=%23MemberFormSlot&member_id=" + member_id;
	new FragmentImporter(url, _initMemberTreeListener).load(url);
}

function _initMemberTreeListener() {
	var slot = document.getElementById("MemberFormSlot");
	addListener(slot, "click", handleMemberTreeViewClick);
    if (browser.isIE55 || browser.isIE6up) {
    	_disableMemberSlotClickHandler = false;
    }
}

function handleMemberTreeViewClick(evt) {
	disableDefault(evt);
	disablePropagation(evt);
	
	// prevent click glitches from IE :((
	if ((browser.isIE55 || browser.isIE6up) && _disableMemberSlotClickHandler)
	    return;
	else {
	    _disableMemberSlotClickHandler = true;
	    setTimeout("_disableMemberSlotClickHandler=false", 100);
	}
	

	var target = getTargetedObject(evt);
	var link, url, query;
	var slot = document.getElementById("MemberFormSlot");
	var afterLoadFunction;
	
	switch (target.tagName) {
		case "IMG" :
			target = target.parentNode;
			afterLoadFunction = _initMemberTreeListener;

		case "A" :
			query = target.href.split('?')[1];
			query = query.replace(/macroName/, "macro");
			query = query.split('#')[0];
			url = portal_url() + "/use_macro?template=gruf_macros&fragmentSelector=%23MemberFormSlot&" + query;
			afterLoadFunction = (afterLoadFunction) ? afterLoadFunction : function() {initForms(slot);};
			new FragmentImporter(url, afterLoadFunction).load();
	}
}