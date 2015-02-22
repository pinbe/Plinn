##parameters=
from Products.Plinn.utils import listWorkflowActions

actions = listWorkflowActions(context)
redirect = context.REQUEST.RESPONSE.redirect
if actions :
	return redirect(actions[0]['url'])
else :
	from ZTUtils import make_query as mq
	from Products.Plinn.utils import transtlate as _
	return redirect('%s?%s' % (actions[0]['url'],
							   mq(portal_status_message = _('You are not allowed to change this content state.'))))