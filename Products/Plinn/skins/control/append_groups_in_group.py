##parameters=groupId, append_groups=[], ajax='', REQUEST=None

gtool = context.portal_groups
group = gtool.getGroupById(groupId)

for id in append_groups :
	group.addGroup(id)

if REQUEST is not None :
	from ZTUtils import make_query as mq
	url = context.portal_url()
	red = REQUEST.RESPONSE.redirect
	return red('%s/groups_members?%s#assign_groups' % (url, mq(group=groupId, ajax=ajax)))