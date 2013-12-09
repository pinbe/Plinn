##parameters=b_start=0, key='', reverse=0, ids=(), items_copy='', items_cut='', items_delete='', items_new='', items_paste='', items_rename='', items_up='', items_down='', items_top='', items_bottom='', items_sort='', template='', macro='', ajax=''
##
from Products.Plinn.PloneMisc import Batch
from DateTime import DateTime
locale_date_fmt = context.locale_date_fmt()
from ZTUtils import make_query
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.permissions import AddPortalContent
from Products.CMFDefault.permissions import DeleteObjects
from Products.CMFDefault.permissions import ListFolderContents
from Products.CMFDefault.permissions import ManageProperties
from Products.CMFDefault.permissions import ViewManagementScreens
from Products.CMFDefault.permissions import ModifyPortalContent
from Products.CMFDefault.utils import html_marshal

mtool = getToolByName(script, 'portal_membership')
checkPermission = mtool.checkPermission
isAnon = mtool.isAnonymousUser()
utool = getToolByName(script, 'portal_url')
portal_url = utool()


form = context.REQUEST.form
default_target = 'object/folderContents'
default_kw = {'b_start': b_start, 'key': key, 'reverse': reverse, 'ajax' : ajax}
if items_copy :
	if ajax : default_kw['syncFragments']=['rightCell']
	if context.validateItemIds(**form) and \
			context.folder_copy_control(**form) and \
			context.setRedirect(context, default_target, **default_kw):
		return
elif items_cut :
	if ajax : default_kw['syncFragments']=['rightCell']
	if context.validateItemIds(**form) and \
			context.folder_cut_control(**form) and \
			context.setRedirect(context, default_target, **default_kw):
			return
elif items_delete and \
		context.validateItemIds(**form) and \
		context.folder_delete_control(**form) and \
		context.setRedirect(context, default_target, **default_kw):
	return
elif items_new and \
		context.setRedirect(context, 'object/new', **default_kw):
	return
elif items_paste :
	if ajax : default_kw['syncFragments']=['rightCell']
	if context.folder_paste_control(**form) and \
			context.setRedirect(context, default_target, **default_kw):
			return
elif items_rename and \
		context.validateItemIds(**form) and \
		context.setRedirect(context, 'object/rename_items', ids=ids,
							**default_kw):
	return
elif items_sort and \
		context.folder_sort_control(**form) and \
		context.setRedirect(context, default_target, b_start=b_start):
	return
elif items_up and \
		context.validateItemIds(**form) and \
		context.folder_up_control(**form) and \
		context.setRedirect(context, default_target, **default_kw):
	return
elif items_down and \
		context.validateItemIds(**form) and \
		context.folder_down_control(**form) and \
		context.setRedirect(context, default_target, **default_kw):
	return
elif items_top and \
		context.validateItemIds(**form) and \
		context.folder_top_control(**form) and \
		context.setRedirect(context, default_target, **default_kw):
	return
elif items_bottom and \
		context.validateItemIds(**form) and \
		context.folder_bottom_control(**form) and \
		context.setRedirect(context, default_target, **default_kw):
	return
	

options = {}

items_add_allowed = checkPermission(AddPortalContent, context)
upitems_list_allowed = checkPermission(ListFolderContents, context, 'aq_parent')
manage_props_allowed = checkPermission(ManageProperties, context)

target = context.getActionInfo(default_target)['url']

if not key:
	(key, reverse) = context.getDefaultSorting()
	is_default = 1
elif (key, reverse) == context.getDefaultSorting():
	is_default = 1
else:
	is_default = 0

columns = ( {'key': 'Type',
			 'title': 'Type',
			 'width': None,
			 'colspan': '2'}
			, {'key': 'id',
			 'title': 'Name',
			 'width': None,
			 'colspan': None}
			, {'key': 'modified',
			 'title': 'Last Modified',
			 'width': None,
			 'colspan': None}
			)

for column in columns:	
	images = []
	if key == column['key'] :
		if not is_default and manage_props_allowed :
			images.append( {'src' : getattr(context, 'set_default_sorting.gif').absolute_url(),
							'alt' : 'Set Sorting as Default',
							'id'	 : 'SetSortingAsDefault',
							'href': '%s?%s' % (target, make_query(items_sort=True,
																  key=key,
																  reverse= (key != 'position' and [reverse] or [False])[0] )
												  )
							 }
							 )

		if key != 'position' :
			if reverse :
				toggleImg = getattr(context, 'arrowDown.gif')
				alt = 'descending sort'
			else :
				toggleImg = getattr(context, 'arrowUp.gif')
				alt = 'ascending sort'
			query = make_query(key=column['key'], reverse = not reverse)
		else :	
			toggleImg = getattr(context, 'arrowUp.gif')
			alt = 'ascending sort'
			query = make_query(key=column['key'])
		images.append( {'src' : toggleImg.absolute_url(), 'alt' : alt} )
	else :
		if key != 'position' :
			query = make_query(key=column['key'], reverse = reverse)
		else :
			query = make_query(key=column['key'])
	
	column['url'] = '%s?%s' % (target, query)
	column['images'] = images

context.filterCookie()
folderfilter = context.REQUEST.get('folderfilter', '')
filter = context.decodeFolderFilter(folderfilter)
items = context.listCatalogedContents(contentFilter=filter)
sort_dir = reverse and 'desc' or 'asc'
sortFunc = key in ['Type'] and 'nocase' or 'cmp'
items = sequence.sort( items, ((key, sortFunc, sort_dir),) )
batch_obj = Batch(items, context.default_batch_size, b_start, orphan=0, quantumleap=1)
items = []
display_delete_button = not isAnon # TODO : à revoir
for item in batch_obj:
	item_icon = item.getIcon
	item_id = item.getId
	item_url = item.getURL()
	items.append(
		{'checkbox': not isAnon,
		 'icon': item_icon and ( '%s/%s' % (portal_url, item_icon) ) or '',
		 'id': item_id,
		 'modified': item.modified.strftime(locale_date_fmt),
		 'title_or_id': item.Title or item_id,
		 'type': item.Type or None,
		 'url': item_url } )

options['batch'] = { 'listColumnInfos': tuple(columns),
					 'listItemInfos': tuple(items),
					 'firstItemPos' : b_start + 1,
					 'sort_key' : key,
					 'sort_dir' : sort_dir,
					 'batch_obj': batch_obj }

hidden_vars = []
for name, value in html_marshal(**default_kw):
	hidden_vars.append( {'name': name, 'value': value} )
	
# buttons
buttons = []
if items_add_allowed and context.allowedContentTypes():
	buttons.append( {'name': 'items_new', 'value': 'New...'} )
	if items:
		buttons.append( {'name': 'items_rename', 'value': 'Rename'} )
		
if checkPermission(ViewManagementScreens, context) and items:
	buttons.append( {'name': 'items_cut', 'value': 'Cut'} )
	buttons.append( {'name': 'items_copy', 'value': 'Copy'} )
	
if items_add_allowed and context.cb_dataValid():
	buttons.append( {'name': 'items_paste', 'value': 'Paste'} )
	
if display_delete_button and items:
	buttons.append( {'name': 'items_delete', 'value': 'Delete'} )

length = batch_obj.sequence_length
is_orderable = manage_props_allowed and (key == 'position') and length > 1
is_sortable = manage_props_allowed and not is_default
options['form'] = { 'action': target,
					'listHiddenVarInfos': tuple(hidden_vars),
					'listButtonInfos': tuple(buttons),
					'is_orderable': is_orderable,
					'is_sortable': is_sortable,
					'items_add_allowed': items_add_allowed }
if not ajax and is_orderable :
	deltas = range( 1, min(5, length) ) + range(5, length, 5)
	options['form']['listDeltas'] = tuple(deltas)

if template and macro :
	options['template'] = template
	options['macro'] = macro
	return context.use_macro(**options)
else :
	return context.folder_contents_template(**options)
