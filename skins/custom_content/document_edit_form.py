##parameters=change='', change_and_view='', ajax=''
##
form = context.REQUEST.form
text = form.get('text')
if text and same_type(text, []) :
	# when javascript is disabled,
	# there's a hidden textarea from epoz
	# and an other from <noscript> tag
	form.update({'text' : text[1]}) 

if change and \
		context.validateTextFile(**form) and \
		context.validateHTML(**form) and \
		context.document_edit_control(**form) and \
		context.setRedirect(context, 'object/edit', **{'ajax':ajax}):
	return
elif change_and_view and \
		context.validateTextFile(**form) and \
		context.validateHTML(**form) and \
		context.document_edit_control(**form) and \
		context.setRedirect(context, 'object/view', **{'ajax':ajax}):
	return


options = {}

buttons = []
target = context.getActionInfo('object/edit')['url']
buttons.append( {'name': 'change', 'value': 'Change'} )
buttons.append( {'name': 'change_and_view', 'value': 'Change and View'} )
options['form'] = { 'action': target,
					'listButtonInfos': tuple(buttons) }

return context.document_edit_template(**options)
