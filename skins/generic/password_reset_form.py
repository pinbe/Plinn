##parameters=validate=''
from Products.CMFCore.utils import getUtilityByInterfaceName
utool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IURLTool')
atool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IActionsTool')

form = context.REQUEST.form
uuid = traverse_subpath[0]

if validate and \
    context.validatePassword(**form) and \
    context.reset_password_control(uuid=uuid, **form) and \
    context.setRedirect(atool, 'user/join', ajax=form.get('ajax')) :
    return

options = {}
options['uuid'] = uuid
options['action'] = '%s/password_reset_form/%s' % (utool(), uuid)

return context.password_reset_template(**options)