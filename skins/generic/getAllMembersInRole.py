##parameters=role

usersAndGroups = context.users_with_local_role(role)
aclu = context.aq_inner.acl_users
prefix = aclu.getGroupPrefix()
mtool = context.portal_membership

users = []
groups = []

for uOrG in usersAndGroups :
	if uOrG.startswith(prefix) :
		groups.append(uOrG)
	else :
		users.append(uOrG)

gtool = context.portal_groups
usersFromGroups = []
for group in  groups :
	usersFromGroups.extend(gtool.getUserNamesOfGroup(group, no_recurse = 0))

allUsersDbl = users
allUsersDbl.extend(usersFromGroups)
allUsers = []
for user in allUsersDbl :
	if user not in allUsers :
		allUsers.append(user)

allMembers = mtool.getMembers(allUsers)
return allMembers