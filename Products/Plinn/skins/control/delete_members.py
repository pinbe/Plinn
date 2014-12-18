##parameters=memberIds=[], ajax=''
if memberIds :
	context.portal_membership.removeMembers(memberIds)
	psm = len(memberIds) == 1 and 'Member deleted.' or 'Members deleted.'
else :
	psm = 'Please select one or more members.'

from ZTUtils import make_query as mq
url = context.portal_url()
red = context.REQUEST.RESPONSE.redirect
return red('%s/portal_members?%s' % (url, mq(portal_status_message=psm, ajax=ajax)))