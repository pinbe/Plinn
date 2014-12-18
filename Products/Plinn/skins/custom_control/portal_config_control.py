##parameters=**kw
##
from Products.CMFCore.utils import getUtilityByInterfaceName
ptool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IPropertiesTool')

ajax_config = (kw.get('ajax_rootClickHandler', 0) and 1) + \
              (kw.get('ajax_autoFormManager', 0) and 2)

kw['ajax_config'] = ajax_config
ptool.editProperties(kw)

return context.setStatus(True, 'CMF Settings changed.')
