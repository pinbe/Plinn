## Script (Python) "various.py"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=site
##title=Import various Plinn setting
##
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.exceptions import BadRequest
from Products.Plinn.exceptions import WorkflowException
# TODO : CMF-2.1 compat
#from Products.PlacelessTranslationService.MessageID import MessageIDFactory
#_ = MessageIDFactory('plinn')
translate = lambda msg : msg
#---


# constructs misc objects
# (productName, factory, id)
misc=(('StandardCacheManagers',	'manage_addAcceleratedHTTPCacheManager',	'HTTPCache'),
	 ('StandardCacheManagers',	'manage_addRAMCacheManager', 				'rcm'),
	 ('GroupUserFolder',		'manage_addGroupUserFolder',				'acl_users'))


dispatcher = site.manage_addProduct
for m in misc :
	try : getattr(dispatcher[m[0]], m[1])(m[2])
	except : pass

if site.acl_users.Users.acl_users.encrypt_passwords :
	site.acl_users.Users.acl_users.manage_setUserFolderProperties(encrypt_passwords=False)


# configure mosaicTool
blockTypes = ('Action Box Block', 'Container Block', 'File Block', 'Image Block', 'Mosaic Document',
			  'Section Block', 'Spacer Block', 'Text Block', 'Tree Box Block')

mostool = getToolByName(site, 'mosaic_tool')
addBI = mostool.manage_addProduct['MosaicDocument'].addMosaicBlockInformation
for bt in blockTypes :
	try : addBI(blockType=bt)
	except BadRequest : pass

# contents
ttool = getToolByName(site, 'portal_types')
wtool = getToolByName(site, 'portal_workflow')

def constructOrSkip(*args, **kw) :
	try : ttool.constructContent(*args, **kw)
	except BadRequest : pass

def addBlockOrSkip(container, *args, **kw) :
	try : container.addBlock(*args, **kw)
	except BadRequest : pass

def doActionForOrSkip(*args, **kw) :
	try : wtool.doActionFor(*args, **kw)
	except WorkflowException : pass
	
# home page
# constructOrSkip(  'Document', site, 'index_html'
# 				, title =	translate('Home')
# 				, text_format='html'
# 				, text=site.default_home_page_content())
# doActionForOrSkip(site.index_html, 'direct_publish')

# default folders
constructOrSkip('Plinn Folder', site, 'Members', title =	translate('Members'))
#constructOrSkip('Plinn Folder', site, 'global_settings', title = translate('Portlets'))
if not hasattr(site, 'global_settings') :
	site.manage_addProduct['OFSP'].manage_addFolder('global_settings')
if not site.global_settings.hasProperty('noIndex'):
	site.global_settings.manage_addProperty('noIndex', True, 'boolean')

# left boxes
constructOrSkip('Mosaic Document', site.global_settings, 'left_boxes', title=translate('Left boxes'))
lb = site.global_settings.left_boxes
addBlockOrSkip(lb, 'Tree Box Block', 0, id='nav_tree')
lb.nav_tree.saveBlock(filteredMetaTypes={'text' : ['Plinn Folder', 'Portfolio', 'Topic']})
doActionForOrSkip(lb, 'direct_publish')

# right boxes
constructOrSkip('Mosaic Document', site.global_settings, 'right_boxes', title=translate('Right boxes'))
rb = site.global_settings.right_boxes
addBlockOrSkip(rb, 'Action Box Block', 0, id='global_actions')
rb.global_actions.saveBlock(boxTitle={'text' : translate('Global actions')}, categories={'text' : ['global']})
addBlockOrSkip(rb, 'Action Box Block', 0, id='workflow_actions')
rb.workflow_actions.saveBlock(boxTitle={'text' : translate('Workflow')}, categories={'text' : ['workflow']})
doActionForOrSkip(rb, 'direct_publish')

# tools settings
mtool = getToolByName(site, 'portal_membership')
mtool.setMemberAreaPortalType('Plinn Folder')

gtool = getToolByName(site, 'portal_groups')
gtool.setGroupWorkspaceContainerType('Plinn Folder')
gtool.setGroupWorkspaceType('Plinn Folder')

caltool = getToolByName(site, 'portal_calendar')
caltool.configureTool(['created', 'modified', 'DateTimeOriginal'], [9, 18])

pimtool = getToolByName(site, 'portal_image_manipulation')
if not pimtool.hasObject('image') :
	pimtool.manage_addProduct['OFSP'].manage_addFolder('image')
if not pimtool.hasObject('tile') :
	pimtool.manage_addProduct['OFSP'].manage_addFolder('tile')

ctool = getToolByName(site, 'portal_catalog')
if not 'position' in ctool.indexes() :
	ctool.manage_addProduct['ProxyIndex'].manage_addProxyIndex('position',
	        extra = { 'idx_type' : 'FieldIndex'
	                , 'value_expr' : 'python:object.getParentNode().getObjectPosition(object.getId())'})

# Caches
HTTPCache = site.HTTPCache
HTTPCache.manage_editProps(title='Accelerated HTTP Cache',
						   settings={'anonymous_only' : False, 'interval' : 3600,'notify_urls' : []})

gtool = getToolByName(site, 'portal_groups')
gtool.ZCacheable_setManagerId('rcm')

return 'Various Plinn settings imported'