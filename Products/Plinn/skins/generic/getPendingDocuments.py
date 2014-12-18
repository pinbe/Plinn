##parameters=
ctool = context.portal_catalog
checkPerm = context.portal_membership.checkPermission
res = []
for s in ['pending'] : # other states can be added
	res.extend(ctool(review_state=s))

pend = []
for b in res :
	ob = b.getObject()
	if checkPerm('Review portal content', ob) :
		pend.append(ob)

return pend
