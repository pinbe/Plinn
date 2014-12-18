##parameters=pos
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Plinn.utils import getAdapterByInterface, translate
def _(message) : return translate(message, context).encode('utf-8')
mtool = getToolByName(context, 'portal_membership')

req = context.REQUEST
resp = req.RESPONSE
form = req.form

req.other['syncFragments'] = ['Breadcrumbs']
options = {}
ctxOptions = {}

history = getAdapterByInterface(context, 'Products.Plinn.interfaces.IContentHistory', None)
key = traverse_subpath[0]

rev, revCtx = history.getHistoricalRevisionByKey(key, withContext=form['pos'])
ctxOptions['rev'] = rev
ctxOptions['currentOb'] = context
ctxOptions['pos'] = pos
ctxOptions['revCtx'] = revCtx
userName = revCtx['current']['user_name']
if userName :
	userId = userName.split()[-1]
	memberFullName = mtool.getMemberFullNameById(userId, nameBefore=False)
else :
	memberFullName = _('nobody')
ctxOptions['ctUser'] = memberFullName
ctxOptions['ctTime'] = revCtx['current']['time'].strftime(_('%Y/%m/%d at %I:%M:%S %p'))
ctxOptions['restorationAllowed'] = mtool.checkPermission(ModifyPortalContent, context)
options['specialCtxHeader'] = context.revision_context_header(**ctxOptions).encode('utf-8')

breadcrumbs = context.breadcrumbs()
breadcrumbs.append(
	{'id' : key
	,'title' : _('state of %s') % revCtx['current']['time'].strftime(_('%Y/%m/%d at %I:%M:%S %p'))
	, 'url' : '%s?pos:int=%d' % (req.ACTUAL_URL, pos)}
	)

options['breadcrumbs'] = breadcrumbs

ti = context.getTypeInfo()
method_id = ti.queryMethodID('view', context=context)
meth = getattr(rev, method_id)
return meth(**options)
