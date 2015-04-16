##parameters=member_id='', given_name='', name='', member_email='', password='', confirm='', add='', ajax=''
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
email_as_login = bool(form.get('email_as_login', True if context.REQUEST.method == 'GET' else False))

if add :
    if validate_email :
        password = confirm = rtool.generatePassword()
        ok = True
    else :
        ok = context.validatePassword(**form)
    if ok :
        try :
            if email_as_login :
                member_id = member_email

            rtool.addMember(id=member_id, password=password,
                            properties={'username': member_id,
                                        'given_name' : given_name,
                                        'name' : name,
                                        'email': member_email})
            if validate_email :
                rtool.requestPasswordReset(member_id, initial=True)
            context.setStatus(True, _('Success!'))
            is_newmember = True
            is_anon = False
        except ValueError, errmsg:
            context.setStatus(False, errmsg)
    
options = {}
options['member_id'] = member_id
options['given_name'] = given_name
options['name'] = name
options['member_email'] = member_email
options['email_as_login'] = email_as_login
options['password'] = is_newmember and context.REQUEST.get('password', '') or ''
options['portal_url'] = portal_url
options['isAnon'] = is_anon
options['isNewMember'] = is_newmember
options['isOrdinaryMember'] = not (mtool.isAnonymousUser() or is_newmember)
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
