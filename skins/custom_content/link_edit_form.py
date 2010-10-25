##parameters=change='', change_and_view='', ajax=''
##
form = context.REQUEST.form
if change and \
		context.link_edit_control(**form) and \
		context.setRedirect(context, 'object/edit', ajax=ajax):
	return
elif change_and_view and \
		context.link_edit_control(**form) and \
		context.setRedirect(context, 'object/view', ajax=ajax):
	return


options = {}

buttons = []
target = context.getActionInfo('object/edit')['url']
#buttons.append( {'name': 'change', 'value': 'Change'} )
buttons.append( {'name': 'change_and_view', 'value': 'Change and View'} )
options['form'] = { 'action': target,
					'listButtonInfos': tuple(buttons) }

options['ajax'] = ajax

return context.link_edit_template(**options)
