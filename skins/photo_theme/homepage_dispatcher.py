##parameters=
from Products.CMFCore.utils import getToolByName
from ZTUtils import make_query as mq
from Products.CMFDefault.utils import Message as _

req = context.REQUEST
resp = req.RESPONSE
came_from = req.form.get('came_from')

if came_from :
	urlQs = came_from.split('?', 1)
	if len(urlQs) == 1 :
		came_from = '%s?%s' % (urlQs[0], mq(portal_status_message=_('Login success')))
	else :
		url, qs=  urlQs
		came_from = '%s?%s&%s' % (url, qs, mq(portal_status_message=_('Login success')))
	return resp.redirect(came_from)

else :
	from Products.realis.utils import searchContentsWithLocalRolesForAuthenticatedUser as search
	results = search(context, portal_type='Portfolio')
	if results :
		atool = getToolByName(context, 'portal_actions')
		return context.setRedirect(atool, 'user/my_albums', portal_status_message=_('Login success'))
	else :
		utool = getToolByName(context, 'portal_url')
		return resp.redirect('%s?%s' % (utool(), mq(portal_status_message=_('Login success'))))
	