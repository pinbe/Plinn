## Script (Python) "logout"
##title=Logout handler
##parameters=ajax=''
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import translate
def _(msg) : return translate(msg, context)
utool = getToolByName(context, 'portal_url')
REQUEST = context.REQUEST
if REQUEST.has_key('portal_skin'):
	context.portal_skins.clearSkinCookie()
REQUEST.RESPONSE.expireCookie('__ac', path='/')
session = REQUEST.SESSION
for k in session.keys() :
	del session[k]
context.setStatus(True, _('You have been logged out.'))
portal = utool.getPortalObject()
return context.setRedirect(portal, 'object/view')