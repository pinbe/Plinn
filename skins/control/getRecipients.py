##parameters=object=None
if object is None :
	object = context
roles = context.valid_roles()

# todo : sort by role

recipientIds = []
rolesAndMembers = []
for role in roles :
	membersInRole = []
	for member in object.getAllMembersInRole(role) :
		if (member.id not in recipientIds) and member.getProperty('email') :
			membersInRole.append(member)
			recipientIds.append(member.id)
	if membersInRole :
		rolesAndMembers.append( (role, membersInRole) )

return rolesAndMembers