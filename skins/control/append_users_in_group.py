##parameters=groupId, append_members=[], ajax='', REQUEST=None

groupsTool = context.portal_groups
group = groupsTool.getGroupById(groupId)

for memberId in append_members :
	group.addMember(memberId)
if REQUEST is not None :
	from ZTUtils import make_query as mq
	red = REQUEST.RESPONSE.redirect
	url = context.portal_url()
	return red('%s/groups_members?%s#assign_members' % (url, mq(group=groupId, ajax=ajax)))