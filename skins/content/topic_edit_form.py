##parameters=addCriterion='', deleteCriteria='', editCriteria='', ajax=''
form = context.REQUEST.form

if addCriterion and \
	context.topic_add_criterion_control(**form) and \
	context.setRedirect(context, 'object/edit', ajax=ajax) :
	return
	
elif deleteCriteria and \
	context.topic_delete_criteria_control(**form) and \
	context.setRedirect(context, 'object/edit', ajax=ajax) :
	return
	
elif editCriteria and \
	context.topic_edit_criteria_control(**form) and \
	context.setRedirect(context, 'object/edit', ajax=ajax) :
	return

options = {'showAcCriteria' : same_type(context.aq_parent, context)}
return context.topic_edit_template(**options)