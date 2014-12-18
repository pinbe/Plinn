##parameters=roles
member = context.portal_membership.getAuthenticatedMember()
for role in roles :
	if member.allowed(context, [role,]) :
		continue
	else :
		return False
return True
