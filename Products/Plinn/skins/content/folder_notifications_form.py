##parameters=save=''
options = {}
from Products.Plinn.utils import getAdapterByInterface

settings = getAdapterByInterface(context, 'Products.Plinn.interfaces.IEmailNotificationSettings')
if save :
	form = context.REQUEST.form
	for interface in settings.getManagedEvents() :
		register = form.get(interface, False)
		settings.subscribeToEvent(interface, register)
	context.setStatus(True, 'Paramètres enregistrés')
	return context.setRedirect(context, 'object/view', ajax=form.get('ajax'))
		
		

options['notifications'] = settings.myNotifications()
return context.folder_notifications_template(**options)