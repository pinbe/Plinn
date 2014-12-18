##parameters=groupId, role, ajax='', REQUEST=None

aclu = context.aq_inner.acl_users
prefix = aclu.getGroupPrefix()
group = context.portal_groups.getGroupById(groupId)
roles = list(group.getUserRoles()[:])
roles.append(role)

try :
	prefixLen = len(prefix)
	groups = [ g[prefixLen:] for g in group.getGroups(no_recurse = 1) ]
except :
	groups = []

aclu.changeUser(groupId, groups = groups, roles = roles )

if REQUEST is not None :
	from ZTUtils import make_query as mq
	url = context.portal_url()
	red = REQUEST.RESPONSE.redirect
	return red('%s/group_data?%s' % (url, mq(group=groupId, ajax=ajax)))
