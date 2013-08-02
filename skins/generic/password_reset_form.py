##parameters=validate=''
from Products.CMFCore.utils import getUtilityByInterfaceName
from Products.Plinn.utils import Message as _
utool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IURLTool')
atool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IActionsTool')

form = context.REQUEST.form
uuid = traverse_subpath[0]

passwordChanged = False

if validate and \
    context.validatePassword(**form) :
    userid = context.reset_password_control(uuid=uuid, **form)
    if userid :
        passwordChanged = True

options = {}
options['uuid'] = uuid
options['passwordChanged'] = passwordChanged
if passwordChanged :
    hidden_vars = ({'name' : '__ac_name',       'value' : userid},
                   {'name' : '__ac_password',   'value' : form['password']},
                   {'name' : 'noAjax',          'value' : '1'})
    target = utool()
    buttons = ({'name': 'login', 'value': _('Login')},)
else :
    hidden_vars = []
    target = '%s/password_reset_form/%s' % (utool(), uuid)
    buttons = ({'name': 'validate', 'value': _('Validate')},)

options['form'] = { 'action': target,
                    'listButtonInfos': tuple(buttons),
                    'listHiddenVarInfos': hidden_vars }


return context.password_reset_template(**options)