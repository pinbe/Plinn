##parameters=ajax=''
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName

eventId = DateTime().strftime("%Y%m%d_%H%M%S")
newOb = getattr(context, context.invokeFactory('Event', eventId, title=' '))

ttool = getToolByName(context, 'portal_types')
ti = ttool.Event
immediate_view = ti.immediate_view

immediate_view = ti.immediate_view
if immediate_view.find('/') > 0 :
	newOb.setStatus('True', 'Object created.')
	return newOb.setRedirect(newOb, immediate_view, ajax=ajax)
else :
	from ZTUtils import make_query
	ob_url = newOb.absolute_url()
	query = make_query(portal_status_message = 'Object created.', ajax = ajax)
	url = "%s/%s?%s" % (ob_url, immediate_view, query)
	return response.redirect(url)