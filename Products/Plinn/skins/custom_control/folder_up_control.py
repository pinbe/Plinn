##parameters=ids, delta, **kw
##

#TODO : translate messages
#from Products.PlacelessTranslationService.MessageID import MessageIDFactory
#_ = MessageIDFactory('default', as_unicode=True)
_ = lambda x : lambda : x

subset_ids = [ obj.getId() for obj in context.listFolderContents() ]
try:
	try:
		attempt = context.moveObjectsUp(ids, delta, subset_ids=subset_ids)
	except TypeError:
		# Zope 2.7.0
		attempt = context.moveObjectsUp(ids, delta)
	if attempt:
		msg = _(attempt == 1 and \
		'%d item moved up.' or \
		'%d items moved up.')().encode('utf-8') % attempt
		return context.setStatus( True, msg)
	else:
		return context.setStatus(False, 'Nothing to change.')
except ValueError, errmsg:
	return context.setStatus(False, 'ValueError: %s' % errmsg)
