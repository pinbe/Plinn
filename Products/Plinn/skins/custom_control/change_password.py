##parameters=password, confirm, domains=None, ajax=''
from ZTUtils import make_query as mq
url = context.portal_url()
red = context.REQUEST.RESPONSE.redirect

mt = context.portal_membership
failMessage=context.portal_registration.testPasswordValidity(password, confirm)
if failMessage:
	return red('%s/password_form?%s' % (url, mq(portal_status_message=failMessage, ajax=ajax)))

member = mt.getAuthenticatedMember()
mt.setPassword(password, domains)
mt.credentialsChanged(password)
return red('%s/personalize_form?%s' % (url, mq(portal_status_message='Password changed.', ajax=ajax)))