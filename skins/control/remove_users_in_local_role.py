##parameters=role, redirect, remove_members=[], ajax=''
from ZTUtils import make_query as mq
red = context.REQUEST.RESPONSE.redirect
url = context.absolute_url()

if remove_members :
	try :
		context.portal_membership.setLocalRoles(context, remove_members, role, remove=1)
	except :
		msg = "You are not allowed to manage this role in this context."
		sd = context.session_data_manager.getSessionData(create = 1)
		sd.update({'roleToManage' : None})
		return red('%s/%s?%s' % (url, redirect, mq(portal_status_message = msg, ajax=ajax)))

return red('%s/%s?%s' % (url, redirect, mq(roleToManage=role, ajax=ajax)))
