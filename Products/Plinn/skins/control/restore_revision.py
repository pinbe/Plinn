##parameters=key, ajax=''
from Products.Plinn.utils import getAdapterByInterface, translate
def _(message) : return translate(message, context).encode('utf-8')
req = context.REQUEST

history = getAdapterByInterface(context, 'Products.Plinn.interfaces.IContentHistory')
history.restore(key)

req.other['portal_status_message'] = _("%(type)s restored.") % {'type':context.getPortalTypeName()}
context.setRedirect(context, 'object/view', ajax=ajax, syncFragments = ['Breadcrumbs'])