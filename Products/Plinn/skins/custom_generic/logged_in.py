##parameters=
##
from Products.CMFCore.utils import getUtilityByInterfaceName
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import decode
from ZTUtils import make_query as mq
from Products.CMFDefault.utils import Message as _

mtool = getToolByName(script, 'portal_membership')
ptool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IPropertiesTool')
stool = getToolByName(script, 'portal_skins')
utool = getToolByName(script, 'portal_url')
atool = getToolByName(script, 'portal_actions')
portal_url = utool()
portal = utool.getPortalObject()


if stool.updateSkinCookie():
	context.setupCurrentSkin()


options = {}

isAnon = mtool.isAnonymousUser()
if isAnon:
	context.REQUEST.RESPONSE.expireCookie('__ac', path='/')
	options['is_anon'] = True
	options['title'] = _(u'Login failure')
	options['admin_email'] = ptool.getProperty('email_from_address')
else:
	mtool.createMemberArea()
	member = mtool.getAuthenticatedMember()
	now = context.ZopeTime()
	last_login = member.getProperty('login_time', None)
	member.setProperties(last_login_time=last_login, login_time=now)
	is_first_login = (last_login == '2000/01/01' and
					  ptool.getProperty('validate_email'))
	if is_first_login:
		member.setProperties(last_login_time='1999/01/01', login_time=now)
		target = '%s/password_form' % portal_url
		context.REQUEST.RESPONSE.redirect(target)
		return
	else:
		member.setProperties(last_login_time=last_login, login_time=now)
		came_from = context.REQUEST.get('came_from', None)
		if came_from:
			return context.REQUEST.RESPONSE.redirect(came_from)
		else :
			url = atool.getActionInfo('user/logged_in', object=portal)['url']
			url = '%s?%s' %(url, mq(portal_status_message=_('Login success')))
			return context.REQUEST.RESPONSE.redirect(url)

return context.logged_in_template(**decode(options, script))
