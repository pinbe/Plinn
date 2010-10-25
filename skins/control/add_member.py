##parameters=username, password, confirm, ajax=''
REQUEST = context.REQUEST
rtool = context.portal_registration
from ZTUtils import make_query as mq
url = context.portal_url()
red = REQUEST.RESPONSE.redirect

failMessage = rtool.testPasswordValidity(password, confirm)
if failMessage :
	return red('%s/portal_members?%s' % (url, mq(portal_status_message = failMessage, ajax=ajax)))

failMessage = rtool.testPropertiesValidity(REQUEST.form)
if failMessage :
	return red('%s/portal_members?%s' % (url, mq(portal_status_message = failMessage, ajax=ajax)))

context.portal_registration.addMember(username, password, roles=[], properties=REQUEST)
red('%s/portal_members?%s' % (url, mq(portal_status_message = 'Member created.', ajax=ajax)))