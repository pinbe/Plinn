##parameters=delete='', empty='', indexes=[], ajax=''
from ZTUtils import make_query
request = context.REQUEST
response = request.RESPONSE

if empty :
	message = 'Clipboard emptied.'
	response.expireCookie('__cp', path=request['BASEPATH1'] or "/")
elif delete :
	if not indexes :
		message = 'Please select one or more items first.'
	elif len(indexes) == 1 :
		message = 'Item removed from clipboard.'
	else :
		message = 'Items removed from clipboard.'
	context.popCP(indexes)


if not ajax:
	redirUrl = request['HTTP_REFERER'].split('?')[0] + \
		   '?' + make_query(portal_status_message=message)
	response.redirect(redirUrl)
else :
    options={}
    options['template'] = 'widgets'
    options['macro'] = 'clipboard'
    options['fragmentId'] = 'clipboard'
    return context.use_macro(**options)