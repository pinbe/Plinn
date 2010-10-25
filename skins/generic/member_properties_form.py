##parameters=memberIds=[], ajax=''

resp = context.REQUEST.RESPONSE
portal_url = context.portal_url()
from ZTUtils import make_query as mq
msg=''

if not memberIds :
	msg = 'Please select a member first.'
	resp.redirect(portal_url + '/portal_members?%s' % mq(portal_status_message=msg, ajax=ajax))
	return

elif len(memberIds) > 1 :
	msg = 'Warning: you should have selected only one member.'

return resp.redirect(portal_url + '/portal_members?%s' % mq(member_id=memberIds[0],
													 portal_status_message=msg,
													 macroName='member_properties_form',
													 ajax=ajax))
