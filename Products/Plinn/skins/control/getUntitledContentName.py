##parameters=

#TODO : translate messages
#from Products.PlacelessTranslationService.MessageID import MessageIDFactory
#_ = MessageIDFactory('plinn')
_ = lambda x : lambda : x

translate = lambda msg : _(msg)().decode('iso-8859-1').encode('utf-8')
portal = context.portal_url.getPortalObject()
ucn = translate(portal.getProperty('untitled_content_name', 'Untitled-'))
ucnl = len(ucn)

untitledNumbers = [ id[ucnl:] for id in context.objectIds() if id.startswith(ucn) ]
nMax = 0
for strN in untitledNumbers :
	try :
		n = int(strN)
		if n > nMax : nMax = n
	except :
		pass

return ucn + str(nMax + 1)