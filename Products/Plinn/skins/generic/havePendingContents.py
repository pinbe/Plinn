##parameters=
ctool = context.portal_catalog
checkPerm = context.portal_membership.checkPermission
from Products.CMFCore.permissions import ReviewPortalContent
for s in ['pending'] : # other states can be added
	for b in ctool(review_state=s) :
		if checkPerm(ReviewPortalContent, b.getObject()) :
			return True
return False