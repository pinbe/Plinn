##parameters=ids=[], items=[], rename='', cancel='', ajax=''
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.utils import html_marshal

utool = getToolByName(script, 'portal_url')
portal_url = utool()


form = context.REQUEST.form
if rename and \
		context.folder_rename_control(**form) and \
		context.setRedirect(context, 'object/folderContents', **form):
	return
elif cancel and \
		context.setRedirect(context, 'object/folderContents', **form):
	return

options = {}
c = context.aq_explicit

if not ids :
    ids = [i['id'] for i in items]
itemInfos = []
for id in ids :
    if hasattr(c, id) :
        item = getattr(c, id)
        if item.cb_isMoveable() :
          item_icon = item.getIcon(1)
          itemInfos.append( { 'icon': item_icon and ( '%s/%s' % (portal_url, item_icon) ) or '',
                              'id': item.getId(),
                              'title': item.Title(),
                              'type': item.Type() or None } )

options['batch'] = { 'listItemInfos': itemInfos }
action = context.getActionInfo('object/rename_items')['url']
buttons = []
buttons.append( {'name': 'rename', 'value': 'Rename'} )
buttons.append( {'name': 'cancel', 'value': 'Cancel'} )
options['form'] = {'action': action,
                   'listButtonInfos': tuple(buttons)}

return context.folder_rename_template(**options)
