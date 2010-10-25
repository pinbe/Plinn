##parameters=ob=None

if ob is None :
	ob = context
wtool = context.portal_workflow
objectActions = filter(lambda a : a.has_key('id'), wtool.getActionsFor(ob))

if not wtool.getInfoFor(ob,'review_state','') == 'published' and  not objectActions :
	return True
else :
	return False