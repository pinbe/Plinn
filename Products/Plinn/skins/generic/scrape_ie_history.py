##parameters=url=''
return '''<html><head>
<script type="text/javascript">
// <!--
	function notifyAjaxLinkHandler() {
		var url = document.body.innerHTML;
		if (window.parent.linkHandler && url)
			window.parent.linkHandler.ie_loadHistory(document.body.innerHTML);
	}
// -->
</script>
</head>
<body onload="notifyAjaxLinkHandler();">%s</body></html>''' % url