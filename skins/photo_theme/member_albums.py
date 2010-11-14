##parameters=

from Products.realis.utils import searchContentsWithLocalRolesForAuthenticatedUser as search

results = search(context, portal_type='Portfolio')
return context.member_albums_template(results = results)