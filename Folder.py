# -*- coding: utf-8 -*-
#######################################################################################
#   Plinn - http://plinn.org                                                          #
#   Copyright (C) 2005-2007  Benoît PIN <benoit.pin@ensmp.fr>                         #
#                                                                                     #
#   This program is free software; you can redistribute it and/or                     #
#   modify it under the terms of the GNU General Public License                       #
#   as published by the Free Software Foundation; either version 2                    #
#   of the License, or (at your option) any later version.                            #
#                                                                                     #
#   This program is distributed in the hope that it will be useful,                   #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of                    #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                     #
#   GNU General Public License for more details.                                      #
#                                                                                     #
#   You should have received a copy of the GNU General Public License                 #
#   along with this program; if not, write to the Free Software                       #
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.   #
#######################################################################################
""" Plinn portal folder implementation



"""

from OFS.CopySupport import CopyError, eNoData, _cb_decode, eInvalid, eNotFound,\
							eNotSupported, sanity_check, cookie_path
from App.Dialogs import MessageDialog
from zExceptions import BadRequest
import sys
import warnings
from cgi import escape
from OFS import Moniker
from ZODB.POSException import ConflictError
import OFS.subscribers
from webdav.NullResource import NullResource
from zope.event import notify
from zope.lifecycleevent import ObjectCopiedEvent
try :
	from zope.app.container.contained import notifyContainerModified
	from zope.app.container.contained import ObjectMovedEvent
except ImportError :
	## Zope-2.13 compat
	from zope.container.contained import notifyContainerModified
	from zope.container.contained import ObjectMovedEvent
from OFS.event import ObjectClonedEvent
from OFS.event import ObjectWillBeMovedEvent
from zope.component.factory import Factory
from Acquisition import aq_base, aq_inner, aq_parent

from types import StringType
from Products.CMFCore.permissions import ListFolderContents, View, ViewManagementScreens,\
										 ManageProperties, AddPortalFolders, AddPortalContent,\
										 ManagePortal, ModifyPortalContent
from permissions import DeletePortalContents, DeleteObjects, DeleteOwnedObjects, SetLocalRoles, CheckMemberPermission
from Products.CMFCore.utils import _checkPermission, getToolByName
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.PortalFolder import PortalFolder, ContentFilter
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl

from zope.interface import implements
from Products.CMFCore.interfaces import IContentish

from utils import _checkMemberPermission
from utils import Message as _
from Globals import InitializeClass
from AccessControl import ClassSecurityInfo


class PlinnFolder(CMFCatalogAware, PortalFolder, DefaultDublinCoreImpl) :
	""" Plinn Folder """
	
	implements(IContentish)

	security = ClassSecurityInfo()
	
	manage_options = PortalFolder.manage_options

	## change security for inherited methods
	security.declareProtected(AddPortalContent, 'manage_pasteObjects')

	def __init__( self, id, title='' ) :
		PortalFolder.__init__(self, id)
		DefaultDublinCoreImpl.__init__(self, title = title)
	
    def __getitem__(self, key):
        if key in self:
            return self._getOb(key, None)
        request = getattr(self, 'REQUEST', None)
        if not isinstance(request, (str, NoneType)):
            method=request.get('REQUEST_METHOD', 'GET')
            if (request.maybe_webdav_client and
                method not in ('GET', 'POST')):
                return NullResource(self, key, request).__of__(self)
        raise KeyError, key
    
		
	security.declarePublic('allowedContentTypes')
	def allowedContentTypes(self):
		"""
		List type info objects for types which can be added in this folder.
		Types can be filtered using the localContentTypes attribute.
		"""
		allowedTypes = PortalFolder.allowedContentTypes(self)
		if hasattr(self, 'localContentTypes'):
			allowedTypes = [t for t in allowedTypes if t.title in self.localContentTypes]
		return allowedTypes

	security.declareProtected(View, 'objectIdCanBeDeleted')
	def objectIdCanBeDeleted(self, id) :
		""" Check permissions and ownership and return True
			if current user can delete object id.
		"""
		if _checkPermission(DeleteObjects, self) : # std zope perm
			return True

		elif _checkPermission(DeletePortalContents, self):
			mtool = getToolByName(self, 'portal_membership')
			authMember = mtool.getAuthenticatedMember()
			ob = getattr(self, id)
			if authMember.allowed(ob, object_roles=['Owner'] ) and \
			   _checkPermission(DeleteOwnedObjects, ob) : return True

		else :
			return False


	security.declareProtected(DeletePortalContents, 'manage_delObjects')
	def manage_delObjects(self, ids=[], REQUEST=None):
		"""Delete subordinate objects.
		   A member can delete his owned contents (if he has the 'Delete Portal Contents' permission)
		   without 'Delete objects' permission in this folder.
		   Return skipped object ids.
		"""
		notOwned = []
		if _checkPermission(DeleteObjects, self) : # std zope perm
			PortalFolder.manage_delObjects(self, ids=ids, REQUEST=REQUEST)
		else :
			mtool = getToolByName(self, 'portal_membership')
			authMember = mtool.getAuthenticatedMember()
			owned = []
			if type(ids) == StringType :
				ids = [ids]
			for id in ids :
				ob = self._getOb(id)
				if authMember.allowed(ob, object_roles=['Owner'] ) and \
				   _checkPermission(DeleteOwnedObjects, ob) : owned.append(id)
				else : notOwned.append(id)
			if owned :
				PortalFolder.manage_delObjects(self, ids=owned, REQUEST=REQUEST)

		if REQUEST is not None:
			return self.manage_main(
				self, REQUEST,
				manage_tabs_message='Object(s) deleted.',
				update_menu=1)
		return notOwned


	security.declareProtected(AddPortalContent, 'manage_renameObjects')
	def manage_renameObjects(self, ids=[], new_ids=[], REQUEST=None) :
		""" Rename subordinate objects
			A member can rename his owned contents if he has the 'Modify Portal Content' permission.
			Returns skippend object ids.
		"""
		if len(ids) != len(new_ids):
			raise BadRequest(_('Please rename each listed object.'))
		
		if _checkPermission(ViewManagementScreens, self) : # std zope perm
			return super(PlinnFolder, self).manage_renameObjects(ids, new_ids, REQUEST)
			
		mtool = getToolByName(self, 'portal_membership')
		authMember = mtool.getAuthenticatedMember()
		skiped = []
		for id, new_id in zip(ids, new_ids) :
			if id == new_id : continue
			
			ob = self._getOb(id)
			if authMember.allowed(ob, object_roles=['Owner'] ) and \
			   _checkPermission(ModifyPortalContent, ob) :
				self.manage_renameObject(id, new_id)
			else :
				skiped.append(id)
		
		if REQUEST is not None :
			return self.manage_main(self, REQUEST, update_menu=1)

		return skiped


	security.declareProtected(ListFolderContents, 'listFolderContents')
	def listFolderContents( self, contentFilter=None ):
		""" List viewable contentish and folderish sub-objects.
		"""
		items = self.contentItems(filter=contentFilter)
		l = []
		for id, obj in items:
			if _checkPermission(View, obj) :
				l.append(obj)

		return l


	security.declareProtected(ListFolderContents, 'listNearestFolderContents')
	def listNearestFolderContents(self, contentFilter=None, userid=None, sorted=False) :
		""" Return folder contents and traverse
		recursively unaccessfull sub folders to find
		accessible contents.
		"""

		filt = {}
		if contentFilter :
			filt = contentFilter.copy()
		ctool = getToolByName(self, 'portal_catalog')
		mtool = getToolByName(self, 'portal_membership')

		if userid and _checkPermission(CheckMemberPermission, getToolByName(self, 'portal_url').getPortalObject()) :
			checkFunc = lambda perm, ob : _checkMemberPermission(userid, View, ob)
			filt['allowedRolesAndUsers'] = ctool._listAllowedRolesAndUsers( mtool.getMemberById(userid) )
		else :
			checkFunc = _checkPermission
			filt['allowedRolesAndUsers'] = ctool._listAllowedRolesAndUsers( mtool.getAuthenticatedMember() )
		
		
		# copy from CMFCore.PortalFolder.PortalFolder._filteredItems
		pt = filt.get('portal_type', [])
		if type(pt) is type(''):
			pt = [pt]
		types_tool = getToolByName(self, 'portal_types')
		allowed_types = types_tool.listContentTypes()
		if not pt:
			pt = allowed_types
		else:
			pt = [t for t in pt if t in allowed_types]
		if not pt:
			# After filtering, no types remain, so nothing should be
			# returned.
			return []
		filt['portal_type'] = pt
		#---

		query = ContentFilter(**filt)
		nearestObjects = []
		
		for o in self.objectValues() :
			if query(o) :
				if checkFunc(View, o):
					nearestObjects.append(o)
				elif getattr(o.aq_self,'isAnObjectManager', False):
					nearestObjects.extend(_getDeepObjects(self, ctool, o, filter=filt))
				
		if sorted and len(nearestObjects) > 0 :
			key, reverse = self.getDefaultSorting()
			if key != 'position' :
				indexCallable = callable(getattr(nearestObjects[0], key))
				if indexCallable :
					sortfunc = lambda a, b : cmp(getattr(a, key)(), getattr(b, key)())
				else :                       
					sortfunc = lambda a, b : cmp(getattr(a, key), getattr(b, key))
				nearestObjects.sort(cmp=sortfunc, reverse=reverse)
		
		return nearestObjects
	
	security.declareProtected(ListFolderContents, 'listCatalogedContents')
	def listCatalogedContents(self, contentFilter={}):
		""" query catalog and returns brains of contents.
			Requires ExtendedPathIndex
		"""
		ctool = getToolByName(self, 'portal_catalog')
		contentFilter['path'] = {'query':'/'.join(self.getPhysicalPath()),
		 						'depth':1}
		return ctool(sort_on='position', **contentFilter)
	

	security.declarePublic('synContentValues')
	def synContentValues(self):
		# value for syndication
		return self.listNearestFolderContents()

	security.declareProtected(View, 'SearchableText')
	def SearchableText(self) :
		""" for full text indexation
		"""
		return '%s %s' % (self.title, self.description)

	security.declareProtected(AddPortalFolders, 'manage_addPlinnFolder')
	def manage_addPlinnFolder(self, id, title='', REQUEST=None):
		"""Add a new PortalFolder object with id *id*.
		"""
		ob=PlinnFolder(id, title)
		# from CMFCore.PortalFolder.PortalFolder :-)
		self._setObject(id, ob)
		if REQUEST is not None:
			return self.folder_contents( # XXX: ick!
				self, REQUEST, portal_status_message="Folder added")

	
#   ## overload to maintain ownership if authenticated user has 'Manage portal' permission
#   def manage_pasteObjects(self, cb_copy_data=None, REQUEST=None):
#   	"""Paste previously copied objects into the current object.
#
#   	If calling manage_pasteObjects from python code, pass the result of a
#   	previous call to manage_cutObjects or manage_copyObjects as the first
#   	argument.
#
#   	Also sends IObjectCopiedEvent and IObjectClonedEvent
#   	or IObjectWillBeMovedEvent and IObjectMovedEvent.
#   	"""
#   	if cb_copy_data is not None:
#   		cp = cb_copy_data
#   	elif REQUEST is not None and REQUEST.has_key('__cp'):
#   		cp = REQUEST['__cp']
#   	else:
#   		cp = None
#   	if cp is None:
#   		raise CopyError, eNoData
#
#   	try:
#   		op, mdatas = _cb_decode(cp)
#   	except:
#   		raise CopyError, eInvalid
#
#   	oblist = []
#   	app = self.getPhysicalRoot()
#   	for mdata in mdatas:
#   		m = Moniker.loadMoniker(mdata)
#   		try:
#   			ob = m.bind(app)
#   		except ConflictError:
#   			raise
#   		except:
#   			raise CopyError, eNotFound
#   		self._verifyObjectPaste(ob, validate_src=op+1)
#   		oblist.append(ob)
#
#   	result = []
#   	if op == 0:
#   		# Copy operation
#   		mtool = getToolByName(self, 'portal_membership')
#   		utool = getToolByName(self, 'portal_url')
#   		portal = utool.getPortalObject()
#   		userIsPortalManager = mtool.checkPermission(ManagePortal, portal)
#
#   		for ob in oblist:
#   			orig_id = ob.getId()
#   			if not ob.cb_isCopyable():
#   				raise CopyError, eNotSupported % escape(orig_id)
#
#   			try:
#   				ob._notifyOfCopyTo(self, op=0)
#   			except ConflictError:
#   				raise
#   			except:
#   				raise CopyError, MessageDialog(
#   					title="Copy Error",
#   					message=sys.exc_info()[1],
#   					action='manage_main')
#
#   			id = self._get_id(orig_id)
#   			result.append({'id': orig_id, 'new_id': id})
#
#   			orig_ob = ob
#   			ob = ob._getCopy(self)
#   			ob._setId(id)
#   			notify(ObjectCopiedEvent(ob, orig_ob))
#   			
#   			if not userIsPortalManager :
#   				self._setObject(id, ob, suppress_events=True)
#   			else :
#   				self._setObject(id, ob, suppress_events=True, set_owner=0)
#   			ob = self._getOb(id)
#   			ob.wl_clearLocks()
#
#   			ob._postCopy(self, op=0)
#
#   			OFS.subscribers.compatibilityCall('manage_afterClone', ob, ob)
#
#   			notify(ObjectClonedEvent(ob))
#
#   		if REQUEST is not None:
#   			return self.manage_main(self, REQUEST, update_menu=1,
#   									cb_dataValid=1)
#
#   	elif op == 1:
#   		# Move operation
#   		for ob in oblist:
#   			orig_id = ob.getId()
#   			if not ob.cb_isMoveable():
#   				raise CopyError, eNotSupported % escape(orig_id)
#
#   			try:
#   				ob._notifyOfCopyTo(self, op=1)
#   			except ConflictError:
#   				raise
#   			except:
#   				raise CopyError, MessageDialog(
#   					title="Move Error",
#   					message=sys.exc_info()[1],
#   					action='manage_main')
#
#   			if not sanity_check(self, ob):
#   				raise CopyError, "This object cannot be pasted into itself"
#
#   			orig_container = aq_parent(aq_inner(ob))
#   			if aq_base(orig_container) is aq_base(self):
#   				id = orig_id
#   			else:
#   				id = self._get_id(orig_id)
#   			result.append({'id': orig_id, 'new_id': id})
#
#   			notify(ObjectWillBeMovedEvent(ob, orig_container, orig_id,
#   										  self, id))
#
#   			# try to make ownership explicit so that it gets carried
#   			# along to the new location if needed.
#   			ob.manage_changeOwnershipType(explicit=1)
#
#   			try:
#   				orig_container._delObject(orig_id, suppress_events=True)
#   			except TypeError:
#   				orig_container._delObject(orig_id)
#   				warnings.warn(
#   					"%s._delObject without suppress_events is discouraged."
#   					% orig_container.__class__.__name__,
#   					DeprecationWarning)
#   			ob = aq_base(ob)
#   			ob._setId(id)
#
#   			try:
#   				self._setObject(id, ob, set_owner=0, suppress_events=True)
#   			except TypeError:
#   				self._setObject(id, ob, set_owner=0)
#   				warnings.warn(
#   					"%s._setObject without suppress_events is discouraged."
#   					% self.__class__.__name__, DeprecationWarning)
#   			ob = self._getOb(id)
#
#   			notify(ObjectMovedEvent(ob, orig_container, orig_id, self, id))
#   			notifyContainerModified(orig_container)
#   			if aq_base(orig_container) is not aq_base(self):
#   				notifyContainerModified(self)
#
#   			ob._postCopy(self, op=1)
#   			# try to make ownership implicit if possible
#   			ob.manage_changeOwnershipType(explicit=0)
#
#   		if REQUEST is not None:
#   			REQUEST['RESPONSE'].setCookie('__cp', 'deleted',
#   								path='%s' % cookie_path(REQUEST),
#   								expires='Wed, 31-Dec-97 23:59:59 GMT')
#   			REQUEST['__cp'] = None
#   			return self.manage_main(self, REQUEST, update_menu=1,
#   									cb_dataValid=0)
#
#   	return result

		
InitializeClass(PlinnFolder)
PlinnFolderFactory = Factory(PlinnFolder)

def _getDeepObjects(self, ctool, o, filter={}):
	res = ctool.unrestrictedSearchResults(path = '/'.join(o.getPhysicalPath()), **filter)
	
	if not res :
		return []
	else :
		deepObjects = []
		res = list(res)
		res.sort(lambda a, b: cmp(a.getPath(), b.getPath()))
		previousPath = res[0].getPath()

		deepObjects.append(res[0].getObject())
		for b in res[1:] :
			currentPath = b.getPath()
			if currentPath.startswith(previousPath) and len(currentPath) > len(previousPath):
				continue
			else :
				deepObjects.append(b.getObject())
				previousPath = currentPath

		return deepObjects


manage_addPlinnFolder = PlinnFolder.manage_addPlinnFolder.im_func
