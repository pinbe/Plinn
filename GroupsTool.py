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
"""
$Id: GroupsTool.py 1332 2008-07-31 12:09:28Z pin $
$URL: http://svn.cri.ensmp.fr/svn/Plinn/branches/CMF-2.1/GroupsTool.py $
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import View, AccessContentsInformation
from Products.CMFCore.utils import getToolByName
from Products.GroupUserFolder.GroupsToolPermissions import ViewGroups, AddGroups, DeleteGroups
from Products.GroupUserFolder.GroupsTool import GroupsTool as BaseTool
from sets import Set
from OFS.SimpleItem import SimpleItem
from OFS.Cache import Cacheable

#Cache view names
CACHE_ROOT_GROUPS = 'getRootGroups'
CACHE_GROUPS_OF_GROUP = 'getGroupsOfGroup'
CACHE_USER_NAMES_OF_GROUP= 'getUserNamesOfGroup'


class GroupsTool(BaseTool, Cacheable) :
	""" Groups tool that behave like Membership tool """
	
	meta_type = 'Plinn Groups Tool'
	
	security = ClassSecurityInfo()
	
	manage_options = BaseTool.manage_options + Cacheable.manage_options
	
	security.declareProtected(AddGroups, 'getGroupWorkspacesCreationFlag')


	def _getUserNamesOfGroup(self, prefixed_group, no_recurse = 1) :
		aclu = self.aq_inner.acl_users
		allUsers = aclu.getPureUsers()
		usersDict = {}
		
		# make a dictionary of users indexed by group
		for user in allUsers :
			for group in user.getGroups(no_recurse = no_recurse) :
				if not usersDict.has_key(group) :
					usersDict[group] = [user.id, ]
				else :
					usersDict[group].append(user.id)
		return usersDict



	security.declareProtected(ViewGroups, 'getUserNamesOfGroup')
	def getUserNamesOfGroup(self, prefixed_group, no_recurse = 1) :
		""" Return users of groups"""
		
		if self.ZCacheable_isCachingEnabled() :
			usersDict = self.ZCacheable_get(view_name=CACHE_USER_NAMES_OF_GROUP,
											keywords={'no_recurse' : no_recurse},
											default=None)
			if usersDict is None :
				# load cache
				usersDict = self._getUserNamesOfGroup(prefixed_group, no_recurse = no_recurse)
				self.ZCacheable_set(usersDict,
									view_name=CACHE_USER_NAMES_OF_GROUP,
									keywords={'no_recurse' : no_recurse})
		else :
			usersDict = self._getUserNamesOfGroup(prefixed_group, no_recurse = no_recurse)

		return usersDict.get(prefixed_group, [])
		

	def _getGroupsOfGroup(self, prefixed_group) :
		aclu = self.aq_inner.acl_users
		
		allGroups = aclu.getGroups()
		groupsDict = {}
		
		# make a dictionary of users indexed by group
		for group in allGroups :
			for superGroup in group.getGroups(no_recurse=1) :
				if not groupsDict.has_key(superGroup) :
					groupsDict[superGroup] = [group.id, ]
				else :
					groupsDict[superGroup].append(group.id)

		return groupsDict
	

	
	security.declareProtected(ViewGroups, 'getGroupsOfGroup')
	def getGroupsOfGroup(self, prefixed_group) :
		""" Return groups of group """
		if self.ZCacheable_isCachingEnabled() :
			groupsDict = self.ZCacheable_get(view_name=CACHE_GROUPS_OF_GROUP, default=None)
			
			if groupsDict is None :
				# load cache
				groupsDict = self._getGroupsOfGroup(prefixed_group)
				self.ZCacheable_set(groupsDict, view_name=CACHE_GROUPS_OF_GROUP)
		else :
			groupsDict = self._getGroupsOfGroup(prefixed_group)
		
		return groupsDict.get(prefixed_group, [])
	
	security.declareProtected(ViewGroups, 'getGroups')
	def getGroups(self, groups) :
		""" Return wrapped groups """
		wGroups = [ self.getGroupById(group) for group in groups ]
		wGroups = filter(None, wGroups)
		
		wGroups.sort(_sortGroup)
		return wGroups
	
	security.declareProtected(ViewGroups, 'getOtherGroups')
	def getOtherGroups(self, groups) :
		""" Return other wrapped groups """
		aclu = self.aq_inner.acl_users
		prefix = aclu.getGroupPrefix()
		allGroupIds = aclu.getGroupNames()

		
		prefixed = 0
		wGroups = []
		if groups :
			if groups[0].startswith(prefix) :
				prefixed = 1

		
			if prefixed :
				prefixLength = len(prefix)
				groups = [ group[prefixLength:] for group in groups ]
	
			for groupId in allGroupIds :
				if groupId not in groups :
					wGroups.append(self.getGroupById(groupId))
		
		else :
			for groupId in allGroupIds :
				wGroups.append(self.getGroupById(groupId))
		
		
		wGroups.sort(_sortGroup)
		return wGroups
		
	
	def _getRootGroups(self) :
		top_level_list = []
		aclu = self.acl_users
		allGroups = aclu.getGroups()
		groupPrefix = aclu.getGroupPrefix()
		
		for group in allGroups :
			if not group.getGroups(no_recurse = 1) :
				top_level_list.append(groupPrefix+group.id)
		return top_level_list

	security.declareProtected(ViewGroups, 'getRootGroups')
	def getRootGroups(self) :
		""" return top level groups """
		if self.ZCacheable_isCachingEnabled() :
			rootGroups = self.ZCacheable_get(view_name=CACHE_ROOT_GROUPS, default=None)
			
			if rootGroups is None :
				rootGroups = self._getRootGroups()
				self.ZCacheable_set(rootGroups, view_name=CACHE_ROOT_GROUPS)
		else :
			rootGroups = self._getRootGroups()

		return rootGroups
		
		
	security.declareProtected(ViewGroups, 'getGroupsWithLocalRole')
	def getGroupsWithLocalRole(self, object, role) :
		""" Return Groups with local role """

		aclu = self.aq_inner.acl_users
		prefix = aclu.getGroupPrefix()
		allGroupNames = aclu.getGroupNames()
		usersAndGroupsWithLocalRole = object.users_with_local_role(role)
		
		return [ gn for gn in usersAndGroupsWithLocalRole if gn.startswith(prefix) ]

	
	security.declareProtected(AddGroups, 'addGroup')
	def addGroup(self, groupName, **mapping):
		""" Create a group, and a group workspace if the toggle is on,
			with the supplied id, roles, and domains.
		"""
		self.acl_users.changeOrCreateGroups(new_groups = [groupName, ])
			
		group = self.getGroupById(groupName)
		group.setGroupProperties(mapping)

		if mapping.get('createArea', None) :
			self.createGrouparea(self.acl_users.getGroupPrefix()+groupName)
		
		if self.ZCacheable_isCachingEnabled() :
			self.ZCacheable_set(None, view_name=CACHE_ROOT_GROUPS)


	security.declareProtected(AddGroups, 'createGrouparea')
	def createGrouparea(self, id):
		"""Create a space in the portal for the given group, much like member home
		folders."""
		
		ttool = getToolByName(self, 'portal_types')
		ti = ttool.getTypeInfo(self.getGroupWorkspaceContainerType())
		
		utool = getToolByName(self, 'portal_url')
		portal = utool.getPortalObject()
		workspaces = self.getGroupWorkspacesFolder()
		if workspaces is None :
			portalOwner = portal.getOwner()
			aclu = self.aq_inner.acl_users
			portalOwner = portalOwner.__of__(aclu)
			workspaces = ti._constructInstance(portal,
											   self.getGroupWorkspacesFolderId(),
											   title=self.getGroupWorkspacesFolderTitle())
			workspaces.manage_delLocalRoles(workspaces.users_with_local_role('Owner'))
			workspaces.changeOwnership(portalOwner)
			ti._finishConstruction(workspaces)


		
		# construct without security check
		group = self.getGroupById(id)
		area = ti._constructInstance(workspaces, id, title=group.getProperty('title', ''))
		
		area.manage_delLocalRoles(area.users_with_local_role('Owner'))
		self.setGroupOwnership(group, area)
		
		ti._finishConstruction(area)


	security.declareProtected(DeleteGroups, 'removeGroups')
	def removeGroups(self, ids, keep_workspaces=0) :
		""" remove the groups and invalidate cache """
		BaseTool.removeGroups(self, ids, keep_workspaces=keep_workspaces)
		if self.ZCacheable_isCachingEnabled() :
			self.ZCacheable_set(None, view_name=CACHE_ROOT_GROUPS)
			self.ZCacheable_set(None, view_name=CACHE_GROUPS_OF_GROUP)
	
	security.declareProtected(ViewGroups, 'getExplAndImplGroupsByUserId')
	def getExplAndImplGroupsByUserId(self, userid) :
		""" Return a dictionary with implicit and explicit wrapped groups """
		aclu = self.aq_inner.acl_users
		user = aclu.getUser(userid)
		if user :
			expl = Set(self.aq_inner.acl_users.getUser(userid).getGroups(no_recurse = 1) or [])
			implDbl = Set(self.aq_inner.acl_users.getUser(userid).getGroups(no_recurse = 0) or [])
			impl = implDbl.difference(expl)
		# wrap
		expl = [self.getGroupById(gid) for gid in expl]
		impl = [self.getGroupById(gid) for gid in impl]
		expl.sort(_sortGroup)
		impl.sort(_sortGroup)
		return {'explicit' : expl,
				'implicit' : impl}
	
InitializeClass(GroupsTool)

	
def _sortGroup(a, b) :
	return cmp(a.id.lower(), b.id.lower())
