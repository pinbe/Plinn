## Script (Python) "content_status_modify"
##parameters=workflow_action, REQUEST=None, **kw
##title=Modify the status of a content object

from ZTUtils import make_query as mq
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.exceptions import zExceptions_Unauthorized

wftool = getToolByName(context, 'portal_workflow')
mtool = getToolByName(context, 'portal_membership')
utool = getToolByName(context, 'portal_url')

if REQUEST :
	kw.update(REQUEST.form)
	
try :
	target = context.getParentNode().getActionInfo('object/view')['url']
except ValueError :
	target = context.getActionInfo('object/view')['url']

res = wftool.doActionFor(context, workflow_action, **kw)
if res :
	# by (Plinn) convention
	# occurs when a ObjectMoved is raised
	kw.update({'syncFragments' : ['Breadcrumbs', 'rightCell']})
	return REQUEST.RESPONSE.redirect('%s?%s' % (res.absolute_url(), mq(**kw)))


kw.update({'portal_status_message' : 'Status changed.'})
try : context.id # touch something in context
except zExceptions_Unauthorized : target = utool()
return REQUEST.RESPONSE.redirect('%s?%s' % (target, mq(**kw)))