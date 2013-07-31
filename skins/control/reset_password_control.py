##parameters=uuid='', password='', confirm='', **kw
from Products.CMFCore.utils import getUtilityByInterfaceName
rtool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IRegistrationTool')

msg = rtool.resetPassword(uuid, password, confirm)
if msg :
    return context.setStatus(False, msg)
else :
    return True