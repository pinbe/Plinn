##parameters=

from Products.Plinn.utils import searchContentsWithLocalRolesForAuthenticatedUser as search

results = search(portal_type='Portfolio')
return context.member_albums_template(results = results)