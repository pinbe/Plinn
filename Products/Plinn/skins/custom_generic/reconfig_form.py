##parameters=change='', ajax=''
##
from Products.CMFCore.utils import getUtilityByInterfaceName
from Products.CMFCore.utils import getToolByName

atool = getToolByName(script, 'portal_actions')
ptool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IPropertiesTool')

form = context.REQUEST.form
if change and \
		context.portal_config_control(**form) and \
		context.setRedirect(atool, 'global/configPortal', ajax=ajax):
	return


options = {}

target = atool.getActionInfo('global/configPortal')['url']
buttons = []
buttons.append( {'name': 'change', 'value': 'Change'} )

ajax_config = ptool.getProperty('ajax_config')
options['form'] = { 'action': target,
					'email_from_name': ptool.getProperty('email_from_name'),
					'email_from_address': ptool.getProperty('email_from_address'),
					'smtp_server': ptool.smtp_server(),
					'title': ptool.title(),
					'description': ptool.getProperty('description'),
					'keywords': '\n'.join(ptool.getProperty('keywords', [])),
					'copyright_notice': ptool.getProperty('copyright_notice'),
					'validate_email': ptool.getProperty('validate_email'),
					'slide_size' : ptool.getProperty('slide_size', ''),
					'listButtonInfos': tuple(buttons),
					'ajax_rootClickHandler' : ajax_config & 1 == 1,
					'ajax_autoFormManager' : ajax_config & 2 == 2 }

return context.reconfig_template(**options)
