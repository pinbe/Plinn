##parameters=change='', change_and_view='', ajax=''
##
form = context.REQUEST.form
if change and \
		context.event_edit_control(**form) and \
		context.setRedirect(context, 'object/edit', ajax=ajax):
	return
elif change_and_view and \
		context.event_edit_control(**form) and \
		context.setRedirect(context, 'object/view', ajax=ajax):
	return


options = {}
buttons = []
formFields = {}

formFields['title']			= form.get('title', context.Title()).strip()
formFields['location']		= form.get('location', context.location)
formFields['contact_name']	= form.get('contact_name', context.contact_name)
formFields['contact_email']	= form.get('contact_email', context.contact_email)
formFields['contact_phone']	= form.get('contact_phone', context.contact_phone)
formFields['event_type']	= form.get('event_type', context.Subject())
formFields['description']	= form.get('description', context.Description())
formFields['event_url']		= form.get('event_url', context.event_url)

start_date = context.start_date and context.start_date or context.end_date
formFields['start_date'] = {'year'	: start_date.year(),
							'month'	: str(start_date.month()).zfill(2),
							'day'	: str(start_date.day()).zfill(2),
							'hour'	: str(start_date.hour()).zfill(2),
							'minute': str(start_date.minute()).zfill(2)}

end_date = context.end_date
formFields['end_date'] = {'year'	: end_date.year(),
						  'month'	: str(end_date.month()).zfill(2),
						  'day'		: str(end_date.day()).zfill(2),
						  'hour'	: str(end_date.hour()).zfill(2),
						  'minute'	: str(end_date.minute()).zfill(2)}



target = context.getActionInfo('object/edit')['url']
buttons.append( {'name': 'change', 'value': 'Change'} )
buttons.append( {'name': 'change_and_view', 'value': 'Change and View'} )
options['form'] = { 'action': target,
					'listButtonInfos': tuple(buttons),
					'fields' : formFields }

#return options['form']['fields']
return context.event_edit_template(**options)
