##parameters=
from Products.CMFCore.utils import getToolByName
from ZTUtils import make_query as mq
from Products.CMFDefault.utils import Message as _

utool = getToolByName(context, 'portal_url')
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

return resp.redirect('%s?%s' % (utool(), mq(portal_status_message=_('Login success'))))