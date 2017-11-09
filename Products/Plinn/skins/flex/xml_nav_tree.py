##parameters=root_name='',expansion='',filter=''
from ZTUtils import SimpleTreeMaker
stm = SimpleTreeMaker()
def replaceXMLEntities(text) :
	for c, ent in (('<', '&lt;'), ('>', '&gt;'), ('&', '&amp;')) :
		text = text.replace(c, ent)
	return text

from string import maketrans
rmBadAttrChars = maketrans('<&"', '   ')

filter = filter.split(',')

childs = list(context.listNearestFolderContents(contentFilter={'portal_type':filter}))
childs.sort(lambda x, y : cmp(x.title_or_id().lower(), y.title_or_id().lower()))

context.REQUEST.RESPONSE.setHeader('content-type', 'text/xml; charset=utf-8')
print '<xml>'
for ob in childs :
	state = 0
	if not getattr(ob, 'isPortalContent', False) :
		state = ob.listNearestFolderContents(contentFilter={'portal_type':filter}) and "-1" or "0"
	row = '<row name="%(name)s" url="%(url)s" icon="%(icon)s" state="%(state)s" description="%(description)s">%(title)s</row>' % {
		  'name' : stm.node(ob).id,
		  'url' : ob.absolute_url(),
		  'title' : replaceXMLEntities(ob.title_or_id()),
		  'description' : ob.Description().translate(rmBadAttrChars),
		  'icon' : ob.getIconURL(),
		  'state' : state
		  }
	print row


print '</xml>'
context.REQUEST.RESPONSE.setCookie('%s-state' % root_name, expansion, path='/')
return printed