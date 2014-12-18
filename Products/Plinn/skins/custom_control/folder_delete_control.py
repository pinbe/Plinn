##parameters=ids, **kw
##title=Delete objects from a folder
##
request = context.REQUEST
response = request.RESPONSE

if request.cookies.has_key('__cp'):
	contextPath = context.getPhysicalPath()
	depth = len(contextPath) + 1
	strContextPath = ''.join(contextPath)

	cp = context.getCPInfo()
	
	deletedObPaths = {}
	for id in ids :
		deletedObPaths[strContextPath + id] = True
	
	indexes, paths = [], cp[1]
	
	for i in range(len(paths)) :
		path = paths[i]
		try :
			firstPart = path[:depth]
			if deletedObPaths.has_key(''.join(firstPart)) :
				indexes.append(i)
		except IndexError : continue

	context.popCP(indexes)
	

ret = context.manage_delObjects( list(ids) )
msg=''
if ret :
	ignored = []
	for id in ret :
		o = getattr(context, id, None)
		if o :
			ignored.append(o.title_or_id())
	#TODO : translate messages
	#from Products.PlacelessTranslationService.MessageID import MessageIDFactory
	#_ = MessageIDFactory('plinn')
	_ = lambda x : lambda : x
	translate = lambda msg : _(msg)().decode('iso-8859-1').encode('utf-8')
	msg = translate('You are not allowed to delete: ') + ', '.join(ignored)

msg = msg or 'Item%s deleted.' % ( len(ids) != 1 and 's' or '' )
return context.setStatus( True,  msg)
