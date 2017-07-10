##parameters=
from Products.CMFCore.utils import getToolByName
from ZTUtils import make_query as mq
from Products.CMFDefault.utils import Message as _

utool = getToolByName(context, 'portal_url')
mtool = getToolByName(script, 'portal_membership')
atool = getToolByName(script, 'portal_actions')

req = context.REQUEST
resp = req.RESPONSE
came_from = req.form.get('came_from')

isAnon = mtool.isAnonymousUser()
if isAnon:
    context.REQUEST.RESPONSE.expireCookie('__ac', path='/')
    return resp.redirect('%s?%s' % (atool.getActionInfo('user/login')['url'], mq(portal_status_message=_('Login failure'))))


if came_from :
    urlQs = came_from.split('?', 1)
    if len(urlQs) == 1 :
        came_from = '%s?%s' % (urlQs[0], mq(portal_status_message=_('Login success')))
    else :
        url, qs=  urlQs
        came_from = '%s?%s&%s' % (url, qs, mq(portal_status_message=_('Login success')))
    return resp.redirect(came_from)

else :
    from Products.Plinn.utils import searchContentsWithLocalRolesForAuthenticatedUser as search
    results = search(portal_type='Portfolio')
    if results :
        atool = getToolByName(context, 'portal_actions')
        return context.setRedirect(atool, 'user/my_albums', portal_status_message=_('Login success'))
    else :
        utool = getToolByName(context, 'portal_url')
        return resp.redirect('%s?%s' % (utool(), mq(portal_status_message=_('Login success'))))
