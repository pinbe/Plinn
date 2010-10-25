## Script (Python) "personalize"
##title=Personalization Handler.
##parameters=
REQUEST=context.REQUEST
member = context.portal_membership.getAuthenticatedMember()

failMessage = context.portal_registration.testPropertiesValidity(REQUEST,
																 member)
if failMessage:
	REQUEST.set('portal_status_message', failMessage)
	return context.personalize_form(context, REQUEST,
									portal_status_message=failMessage)

member.setProperties(REQUEST)
#photo_width = REQUEST['photo_width']
#context.getOrSetSessionVar(key = 'preferedImageSize', value=(photo_width, photo_width))

if REQUEST.has_key('portal_skin'):
	context.portal_skins.updateSkinCookie()

from ZTUtils import make_query as mq
params = {'portal_status_message' : 'Saved changes.'}
if REQUEST.has_key('ajax') :
	params['ajax'] = '1'
qs = mq(**params)

context.REQUEST.RESPONSE.redirect('%s/personalize_form?%s' % (context.portal_url(), qs))
