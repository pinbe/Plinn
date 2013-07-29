##parameters=userid='', requestReset=''
from Products.CMFCore.utils import getUtilityByInterfaceName
from Products.Plinn.utils import Message as _
utool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IURLTool')
rtool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IRegistrationTool')

if requestReset :
    uuid = rtool.requestPasswordReset(userid)
    context.setStatus(True, _('request for resetting password sent'))
    return 'yeah !'

options={}
target = '%s/request_password_reset_form' % utool()
options['action'] = target

return context.request_password_reset_template(**options)