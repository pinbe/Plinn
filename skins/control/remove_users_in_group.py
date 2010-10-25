##parameters=groupId, remove_members=[], ajax='', REQUEST=None
groupsTool = context.portal_groups
group = groupsTool.getGroupById(groupId)

for memberId in remove_members :
	group.removeMember(memberId)
if REQUEST is not None :
	return context.REQUEST. RESPONSE.redirect('%s/groups_members?group=%s&ajax=%s#assign_members' % (context.portal_url(), groupId, ajax))