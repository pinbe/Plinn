##parameters=groupId, roles=[], ajax='', REQUEST=None

aclu = context.aq_inner.acl_users
prefix = aclu.getGroupPrefix()
group = context.portal_groups.getGroupById(groupId)
newRoles = [role for role in group.getUserRoles() if role not in roles]

try :
	prefixLen = len(prefix)
	groups = [ g[prefixLen:] for g in group.getGroups(no_recurse = 1) ]
except :
	groups = []

aclu.changeUser(groupId, groups = groups, roles = newRoles )

if REQUEST is not None :
	from ZTUtils import make_query as mq
	url = context.portal_url()
	red = REQUEST.RESPONSE.redirect
	return red('%s/group_data?%s' % (url, mq(group=groupId, ajax=ajax)))