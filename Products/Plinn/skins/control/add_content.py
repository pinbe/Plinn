##parameters=
from Products.Plinn.utils import makeValidId
form = context.REQUEST.form
from Products.CMFCore.utils import getToolByName
handler = getToolByName(context, 'portal_uidhandler')

for k in form.keys() :
	item = form[k]
	if hasattr(item, 'keys') and item.has_key('type') :
		typeDic = item.copy()
		typeDic['type'] = k
		break

if typeDic.has_key('id') :
	title = typeDic['id']
	newid = makeValidId(context, title)

	context.invokeFactory( typeDic['type'], newid, title=title)
	newOb = getattr(context, newid)
	handler = getToolByName(context, 'portal_uidhandler')
	handler.register(newOb)
	ti = newOb.getTypeInfo()
	immediate_view = ti.immediate_view

	if immediate_view.find('/') > 0 :
		newOb.setStatus('True', 'Object created.')
		return newOb.setRedirect(newOb, immediate_view, syncFragments = ['Breadcrumbs', 'rightCell'], **form)
	else :
		from ZTUtils import make_query
		ob_url = newOb.absolute_url()
		query = make_query(portal_status_message = 'Object created.', ajax = form.get('ajax'), syncFragments = ['Breadcrumbs', 'rightCell'])
		url = "%s/%s?%s" % (ob_url, immediate_view, query)
		response = context.REQUEST.RESPONSE
		return response.redirect(url)
		
elif typeDic.has_key('create_form') :
	from Products.CMFCore.utils import getToolByName
	ttool = getToolByName(context, 'portal_types')
	typeName = typeDic['type']
	ti = getattr(ttool, typeName)
	ai = ti.getActionInfo('object/create', object=context)
	url = ai['url']

	from ZTUtils import make_query
	query = make_query(ajax=form.get('ajax'))
	url = '%s?%s' % (url, query)
	response = context.REQUEST.RESPONSE
	return response.redirect(url)
