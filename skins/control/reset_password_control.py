##parameters=uuid='', password='', confirm='', **kw
from Products.CMFCore.utils import getUtilityByInterfaceName
rtool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IRegistrationTool')

userid, msg  = rtool.resetPassword(uuid, password, confirm)
if msg :
    context.setStatus(False, msg)

return userid