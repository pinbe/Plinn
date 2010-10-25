##parameters=
parent = context.aq_parent
req = context.REQUEST
assert req.method == 'POST', "This script works only in POST http method"

req.RESPONSE.setHeader('Content-Type', 'text/xml;charset=utf-8')

try :
	parent.manage_delObjects(context.id)
except Exception, e :
	return '<error>%s</error>' % str(e)

return '<done/>'