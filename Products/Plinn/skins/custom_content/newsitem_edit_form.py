##parameters=change='', change_and_view='', ajax=''
##
form = context.REQUEST.form
description = form.get('description')
if description and same_type(description, []) :
	# when javascript is disabled,
	# there's a hidden textarea from epoz
	# and an other from <noscript> tag
	form.update({'description' : description[1],
				 'text' : form['text'][1]})
 
if change and \
		context.validateHTML(**form) and \
		context.newsitem_edit_control(**form) and \
		context.setRedirect(context, 'object/edit', **{'ajax':ajax}):
	return
elif change_and_view and \
		context.validateHTML(**form) and \
		context.newsitem_edit_control(**form) and \
		context.setRedirect(context, 'object/view', **{'ajax':ajax}):
	return


options = {}

buttons = []
target = context.getActionInfo('object/edit')['url']
buttons.append( {'name': 'change', 'value': 'Change'} )
buttons.append( {'name': 'change_and_view', 'value': 'Change and View'} )
options['form'] = { 'action': target,
					'listButtonInfos': tuple(buttons) }

return context.newsitem_edit_template(**options)
