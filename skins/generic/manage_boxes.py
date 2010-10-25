##parameters=exitMode=False
sd = context.session_data_manager.getSessionData(create=1)
if exitMode :
	if sd.has_key('editBoxes') : del sd['editBoxes']
	if sd.has_key('ajaxConfig') : del sd['ajaxConfig']
else :
	sd['editBoxes'] = 1
	sd['ajaxConfig'] = 0
return context.portal_url.getPortalObject().index_html()