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
$Id: GroupDataTool.py 1261 2008-01-07 01:34:23Z pin $
$URL: http://svn.cri.ensmp.fr/svn/Plinn/branches/CMF-2.1/GroupDataTool.py $
"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_parent, aq_base

from Products.GroupUserFolder.GroupDataTool import GroupDataTool as BaseTool
from Products.GroupUserFolder.GroupDataTool import GroupData as BaseGroupData
from Products.GroupUserFolder.GroupsToolPermissions import ManageGroups, ViewGroups
from Products.CMFCore.utils import getToolByName
from ZPublisher.Converters import type_converters

from GroupsTool import CACHE_ROOT_GROUPS, CACHE_GROUPS_OF_GROUP, CACHE_USER_NAMES_OF_GROUP

try:
	from Products.CMFCore.MemberDataTool import CleanupTemp
	_have_cleanup_temp = 1
except:
	_have_cleanup_temp = None


class GroupDataTool(BaseTool) :
	""" Group Data Tool """
	
	meta_type = 'Plinn Group Data Tool'
	
	security = ClassSecurityInfo()
	
	security.declarePrivate('wrapGroup')
	def wrapGroup(self, g):
		"""Returns an object implementing the GroupData interface"""
		id = g.getId()
		members = self._members
		if not members.has_key(id):
			# Get a temporary member that might be
			# registered later via registerMemberData().
			temps = self._v_temps
			if temps is not None and temps.has_key(id):
				portal_group = temps[id]
			else:
				base = aq_base(self)
				portal_group = GroupData(base, id)
				if temps is None:
					self._v_temps = {id:portal_group}
					if hasattr(self, 'REQUEST'):
						# No REQUEST during tests.
						# XXX jcc => CleanupTemp doesn't seem to work on Plone 1.0.3.
						# Have to find a way to pass around...
						if _have_cleanup_temp:
							self.REQUEST._hold(CleanupTemp(self))
				else:
					temps[id] = portal_group
		else:
			portal_group = members[id]
		# Return a wrapper with self as containment and
		# the user as context.
		return portal_group.__of__(self).__of__(g)

class GroupData(BaseGroupData) :
	"""	 """
	
	security = ClassSecurityInfo()
	
	security.declareProtected(ViewGroups, 'getGroups')
	security.declareProtected(ManageGroups, 'setGroupProperties')
	def setGroupProperties(self, mapping):
		'''Sets the properties of the group.
		'''
		# Sets the properties given in the MemberDataTool.
		tool = self.getTool()
		self = self.aq_inner.aq_self
		for id in tool.propertyIds():
			if mapping.has_key(id):
				if not self.__class__.__dict__.has_key(id):
					value = mapping[id]
					if type(value)==type(''):
						proptype = tool.getPropertyType(id) or 'string'
						if type_converters.has_key(proptype):
							value = type_converters[proptype](value)
					setattr(self, id, value)
		# Hopefully we can later make notifyModified() implicit.
		self.notifyModified()
	
	security.declareProtected(ManageGroups, 'removeMember')
	def removeMember(self, id):
		""" Remove the member with the provided id from the group """
		
		user = self.acl_users.getUser(id)
		
		groups = list(user.getGroups(no_recurse=1))
		prefix = self.acl_users.getGroupPrefix()
		try : groups.remove(prefix + self.getGroupName())
		except ValueError : return # the user (id) is an implicit member of this group (self)
		
		roles_no_recurse = tuple(filter(lambda x: x not in ('Authenticated', 'Shared'), user.getUserRoles()))
		
		if user.isGroup() :
			self.acl_users._doChangeGroup(id, roles_no_recurse, groups = groups)
		else :
			self.acl_users._doChangeUser(id,
										 None,
										 roles_no_recurse,
										 user.getDomains(),
										 groups=tuple(groups))
		
		gtool = getToolByName(self, "portal_groups")
		if gtool.ZCacheable_isCachingEnabled() :
			# humm... there's a bug on Cacheable / RamCacheManger
			#gtool.ZCacheable_invalidate(view_name=CACHE_USER_NAMES_OF_GROUP)
			gtool.ZCacheable_set(None, view_name=CACHE_USER_NAMES_OF_GROUP, keywords={'no_recurse' : 0})
			gtool.ZCacheable_set(None, view_name=CACHE_USER_NAMES_OF_GROUP, keywords={'no_recurse' : 1})

	

	security.declareProtected(ManageGroups, 'addMember')
	def addMember(self, id):
		""" Add the existing member with the given id to the group"""
		aclu = self.aq_inner.acl_users
		user = aclu.getUser(id)
		prefix = aclu.getGroupPrefix()
		
		userRoles = tuple(filter(lambda x: x not in ('Authenticated', 'Shared'), user.getUserRoles()))
		groups = user.getGroups(no_recurse = 1)
		groups += (self.id, )
		
		aclu.changeUser(user.id, groups = groups, roles = userRoles)
		gtool = getToolByName(self, 'portal_groups')
		if gtool.ZCacheable_isCachingEnabled() :
			# humm... there's a bug on Cacheable / RamCacheManger
			#gtool.ZCacheable_invalidate(view_name=CACHE_USER_NAMES_OF_GROUP)
			gtool.ZCacheable_set(None, view_name=CACHE_USER_NAMES_OF_GROUP, keywords={'no_recurse' : 0})
			gtool.ZCacheable_set(None, view_name=CACHE_USER_NAMES_OF_GROUP, keywords={'no_recurse' : 1})



	security.declareProtected(ManageGroups, 'removeGroup')
	def removeGroup(self, id) :
		""" Remove the existing group with the given id to the group"""
		aclu = self.aq_inner.acl_users
		groupPrefix = aclu.getGroupPrefix()
		group = aclu.getGroup(id)
		
		# get group roles
		groupRoles = tuple(filter(lambda x: x not in ('Authenticated', 'Shared'), group.getUserRoles()))
		superGroupIds = list(group.getGroups(no_recurse = 1))
		superGroupIds.remove(self.id)
		
		aclu.changeUser(groupPrefix + group.id, groups = superGroupIds, roles = groupRoles)

		gtool = getToolByName(self, "portal_groups")
		if gtool.ZCacheable_isCachingEnabled() :
			gtool.ZCacheable_set(None, view_name=CACHE_GROUPS_OF_GROUP)
			if not superGroupIds :
				gtool.ZCacheable_set(None, view_name=CACHE_ROOT_GROUPS)


	security.declareProtected(ManageGroups, 'addGroup')
	def addGroup(self, id) :
		""" Add the existing group with the given id to the group"""
		aclu = self.aq_inner.acl_users
		groupPrefix = aclu.getGroupPrefix()
		group = aclu.getGroup(id)
		
		# get group roles
		groupRoles = tuple(filter(lambda x: x not in ('Authenticated', 'Shared'), group.getUserRoles()))
		superGroupIds = list(group.getGroups(no_recurse = 1))
		newSuperGroupIds = superGroupIds[:]
		newSuperGroupIds.append(self.id)
		
		aclu.changeUser(groupPrefix + group.id, groups = newSuperGroupIds, roles = groupRoles)
		
		gtool = getToolByName(self, "portal_groups")
		if gtool.ZCacheable_isCachingEnabled() :
			gtool.ZCacheable_set(None, view_name=CACHE_GROUPS_OF_GROUP)
			if not superGroupIds :
				gtool.ZCacheable_set(None, view_name=CACHE_ROOT_GROUPS)
				


InitializeClass(GroupDataTool)
