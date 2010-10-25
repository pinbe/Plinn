##parameters=groupId, remove_groups=[], ajax='', REQUEST=None

gtool = context.portal_groups
group = gtool.getGroupById(groupId)

for id in remove_groups :
	group.removeGroup(id)

if REQUEST is not None :
	return context.REQUEST. RESPONSE.redirect('%s/groups_members?group=%s&ajax=%s#assign_groups' % (context.portal_url(), groupId, ajax))