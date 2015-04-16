##parameters=member_id='', given_name='', name='', member_email='', email_as_login='', password='', confirm='', add='', ajax=''
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.permissions import ManageUsers
from Products.Plinn.RegistrationTool import MODE_ANONYMOUS, MODE_REVIEWED
from Products.Plinn.utils import translate
def _(message) : return translate(message, context).encode('utf-8')


mtool = getToolByName(script, 'portal_membership')
ptool = getToolByName(script, 'portal_properties')
rtool = getToolByName(script, 'portal_registration')
atool = getToolByName(script, 'portal_actions')
utool = getToolByName(script, 'portal_url')
portal_url = utool()
validate_email = ptool.getProperty('validate_email')
is_anon = mtool.isAnonymousUser()
is_newmember = False
is_usermanager = mtool.checkPermission(ManageUsers, mtool)


form = context.REQUEST.form

if add :
    if validate_email :
        password = confirm = rtool.generatePassword()
    else :
        ok = context.validatePassword(**form)
    try :
        if email_as_login :
            member_id = member_email
    	rtool.addMember(id=member_id, password=password,
    					properties={'username': member_id,
    								'given_name' : given_name,
    								'name' : name,
    								'email': member_email})
        context.setStatus(True, _('Success!'))
    except ValueError, errmsg:
    	context.setStatus(False, errmsg)
    
        

# if add and \
#         context.validatePassword(**form) and \
#         context.members_add_control(**form) and \
#         context.setRedirect(atool, 'user/join', b_start=b_start, ajax=ajax):
#     return

options = {}

if context.REQUEST.get('portal_status_message', '') == 'Success!':
	is_anon = False
	is_newmember = True

options['member_id'] = member_id
options['given_name'] = given_name
options['name'] = name
options['member_email'] = member_email
options['password'] = is_newmember and context.REQUEST.get('password', '') or ''
options['portal_url'] = portal_url
options['isAnon'] = is_anon
options['isNewMember'] = is_newmember
options['validate_email'] = validate_email
options['isAnonRegistration'] = rtool.getMode() == MODE_ANONYMOUS
options['isReviewedRegistration'] = rtool.getMode() == MODE_REVIEWED

buttons = []
if is_newmember:
	target = atool.getActionInfo('user/logged_in')['url']
	buttons.append( {'name': 'login', 'value': 'Log in'} )
else:
	target = atool.getActionInfo('user/join')['url']
	buttons.append( {'name': 'add', 'value': _('Join')} )
options['form'] = { 'action': target,
					'listButtonInfos': tuple(buttons) }
options['ajax']=ajax
return context.join_template(**options)
