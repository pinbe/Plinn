##parameters=role
aclu = context.aq_inner.acl_users
prefix = aclu.getGroupPrefix()
allGroupNames = aclu.getGroupNames()
usersAndGroupsWithLocalRole = context.users_with_local_role(role)

groupsWithLocalRole = [ gn for gn in usersAndGroupsWithLocalRole if gn.startswith(prefix) ]

groupsWithoutLocalRole = [ gn for gn in allGroupNames if gn not in groupsWithLocalRole ]

getGroupById = context.portal_groups.getGroupById


def sortOnTitleOrId(m0, m1) :
	return cmp(m0.title_or_id().lower(), m1.title_or_id().lower())

insideList = map(getGroupById, groupsWithLocalRole)
outsideList = map(getGroupById, groupsWithoutLocalRole)

insideList.sort(sortOnTitleOrId)
outsideList.sort(sortOnTitleOrId)

groupsDict = {'inside'	: insideList,
			  'outside' : outsideList}

return groupsDict