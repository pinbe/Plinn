// (c) Benoît PIN 2006-2007
// http://plinn.org
// Licence GPL
// $Id: epoz_plinn.js 1315 2008-07-29 15:36:15Z pin $
// $URL: http://svn.cri.ensmp.fr/svn/Plinn/branches/CMF-2.1/skins/ajax_scripts/epoz_plinn.js $

function _resetEpoz() {
	form_path = absolute_url() + '/';
	EpozElement = null;
	EpozTextArea = null;
}

function initEpozWidget(iframe) {
	var toolBar = iframe.parentNode;
	var ta = toolBar.nextSibling; // ta -> textarea
	var name = ta.name;
	
	// change ids
	iframe.id = IFramePrefix + name;
	iframe.contentWindow.document.id = DocPrefix + name;
	toolBar.id = ToolBarPrefix + name;
	var checkbox = ta.nextSibling.childNodes[0];
	checkbox.id = CheckBoxPrefix + name;
	
    // populate iframe's document
    iframe.contentWindow.document.body.innerHTML = ta.value;
	addListener(iframe, "click", HandleEpozRedirect);

	if (browser.isGecko) {
		scriptExpr = 'EnableDesignMode("' + iframe.id + '");';
		window.setTimeout(scriptExpr, 10);
	}
	
	toolBar.style.display = "inline";
	checkbox.parentNode.style.display = "inline";
	changeBorderStyle(iframe, "dashed");
}
