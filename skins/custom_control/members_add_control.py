##parameters=member_id, given_name, name, password, member_email, send_password=False, **kw
##title=Add a member
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.permissions import ManageUsers
from Products.Plinn.RegistrationTool import MODE_REVIEWED

mtool = getToolByName(script, 'portal_membership')
ptool = getToolByName(script, 'portal_properties')
rtool = getToolByName(script, 'portal_registration')

try:
	rtool.addMember( id=member_id, password=password,
					 properties={'username': member_id,
								 'given_name' : given_name,
								 'name' : name,
								 'email': member_email} )
except ValueError, errmsg:
	return context.setStatus(False, errmsg)
else:
	if send_password or (ptool.getProperty('validate_email') and rtool.getMode() != MODE_REVIEWED):
		rtool.registeredNotify(member_id)
	if mtool.checkPermission(ManageUsers, mtool):
		return context.setStatus(True, 'Member registered.')
	else:
		return context.setStatus(False, 'Success!')
