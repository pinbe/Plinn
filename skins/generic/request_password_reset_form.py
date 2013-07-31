##parameters=userid='', requestReset='', ajax=''
from Products.CMFCore.utils import getUtilityByInterfaceName
from Products.Plinn.utils import Message as _
utool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IURLTool')
rtool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IRegistrationTool')

if requestReset :
    msg = rtool.requestPasswordReset(userid)
    if not  msg :
        context.setStatus(True, _('Request for resetting password sent to your contact email.'))
        context.setRedirect(utool.getPortalObject(), 'object/view', ajax=ajax)
        return
    
    context.setStatus(False, msg)

options={}
target = '%s/request_password_reset_form' % utool()
options['action'] = target

return context.request_password_reset_template(**options)