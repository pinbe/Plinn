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
from Products.Plinn.utils import translate as i18ntranslate
translate = lambda msg : i18ntranslate(msg, context)


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
	site.acl_users.Users.acl_users.manage_setUserFolderProperties(encrypt_passwords=True)


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
text=[]
text.append('<h1>%s</h1>' % translate('Welcome to Plinn!'))
text.append('<p>%s</p>' % translate('This is the default home page.'))
text.append('<p>%s</p>' % translate('To change the content just select "Edit" in the Tab bar on the top.'))
text = '\n'.join(text)
constructOrSkip(  'Document', site, 'index_html'
				, title =	translate('Home')
				, text_format='html'
				, text=text)
doActionForOrSkip(site.index_html, 'direct_publish')

# default folders
constructOrSkip('Huge Plinn Folder', site, 'Members', title =	translate('Members'))


# tools settings
mtool = getToolByName(site, 'portal_membership')
mtool.setMemberAreaPortalType('Huge Plinn Folder')

gtool = getToolByName(site, 'portal_groups')
gtool.setGroupWorkspaceContainerType('Huge Plinn Folder')
gtool.setGroupWorkspaceType('Huge Plinn Folder')

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