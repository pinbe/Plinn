##parameters=username, password='', confirm='', ajax=''

from ZTUtils import make_query as mq
portal_url = context.portal_url()
rtool = context.portal_registration
req=context.REQUEST
resp = req.RESPONSE
member = context.portal_membership.getMemberById(username)

failMessage = rtool.testPropertiesValidity(req, member)
if failMessage:
	return resp.redirect(portal_url + '/portal_members?%s' % mq(portal_status_message=failMessage,
																member_id=username,
																macroName='member_properties_form',
																ajax=ajax))

member.setMemberProperties(req.form)

if password :
	failMessage = rtool.testPasswordValidity(password, confirm=confirm)
	if failMessage:
		return resp.redirect(portal_url + '/portal_members?%s' % mq(portal_status_message=failMessage,
																	member_id=username,
																	macroName='member_properties_form',
																	ajax=ajax))
	else :
		member.setMemberPassword(password)

return resp.redirect(portal_url + '/portal_members?%s' % mq(portal_status_message='Member modified.', ajax=ajax))