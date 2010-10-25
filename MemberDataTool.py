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
""" Workflow aware MemberData to provide reviewed member registration.

$Id: MemberDataTool.py 1316 2008-07-29 15:37:23Z pin $
$URL: http://svn.cri.ensmp.fr/svn/Plinn/branches/CMF-2.1/MemberDataTool.py $
"""

from Globals import InitializeClass
from Acquisition import aq_inner, aq_parent, aq_base
from AccessControl import ClassSecurityInfo
from Products.CMFCore.MemberDataTool import MemberDataTool as BaseTool
from Products.CMFCore.MemberDataTool import MemberData as BaseData
from Products.CMFCore.MemberDataTool import CleanupTemp
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
from Products.CMFCore.DynamicType import DynamicType
from utils import formatFullName
from permissions import SetMemberProperties, SetMemberPassword


class MemberDataTool (BaseTool):
	""" This tool wraps user objects, making them act as Member objects.
	"""

	meta_type = 'Plinn Member Data Tool'
##		 __implements__ = (IMemberDataTool, ActionProviderBase.__implements__)
	
	security = ClassSecurityInfo()

	def __init__(self):
		BaseTool.__init__(self)
		# Create the default properties.
		self._setProperty('name', '', 'string')
		self._setProperty('given_name', '', 'string')
		self._setProperty('wysiwyg_editor', 'FCK', 'string')
		self._setProperty('photo_width', 800, 'int')

	security.declarePrivate('wrapUser')
	def wrapUser(self, u):
		'''
		If possible, returns the Member object that corresponds
		to the given User object.
		'''
		id = u.getId()
		members = self._members
		if not id in members:
			base = aq_base(self)
			members[id] = MemberData(base, id)
		# Return a wrapper with self as containment and
		# the user as context.
		return members[id].__of__(self).__of__(u)

#	security.declarePrivate('wrapUser')
#	def wrapUser(self, u):
#		"""
#		If possible, returns the Member object that corresponds
#		to the given User object.
#		"""
#		id = u.getId()
#		members = self._members
#		if not members.has_key(id):
#			# Get a temporary member that might be
#			# registered later via registerMemberData().
#			temps = self._v_temps
#			if temps is not None and temps.has_key(id):
#				m = temps[id]
#			else:
#				base = aq_base(self)
#				m = MemberData(base, id)
#				if temps is None:
#					self._v_temps = {id:m}
#					if hasattr(self, 'REQUEST'):
#						# No REQUEST during tests.
#						self.REQUEST._hold(CleanupTemp(self))
#				else:
#					temps[id] = m
#		else:
#			m = members[id]
#		# Return a wrapper with self as containment and
#		# the user as context.
#		return m.__of__(self).__of__(u)


	def __bobo_traverse__(self, REQUEST, name):
		if hasattr(self,name):
			return getattr(self,name)
		else:
			if self._members.has_key(name) :
				return self.wrapUser(self.acl_users.getUser(name))

InitializeClass(MemberDataTool)


class MemberData (BaseData, DynamicType, CMFCatalogAware):

##		 __implements__ = IMemberData

	portal_type = 'Member Data'

	security = ClassSecurityInfo()

	security.declareProtected(SetMemberPassword, 'setMemberPassword')
	def setMemberPassword(self, password, domains=None) :
		""" set member password """

		registration = getToolByName(self, 'portal_registration', None)
		if registration:
			failMessage = registration.testPasswordValidity(password)
			if failMessage is not None:
				raise 'Bad Request', failMessage
				
		user_folder = self.acl_users
		self.setSecurityProfile(password=password, domains=domains)
		if user_folder.meta_type == 'Group User Folder' :
			self.changePassword(password)
	
	
	#XXX restore the previous implementation for GRUF 2 I'll remove that later...
	security.declarePrivate('setSecurityProfile')
	def setSecurityProfile(self, password=None, roles=None, domains=None):
		"""Set the user's basic security profile"""
		u = self.getUser()
		# This is really hackish.  The Zope User API needs methods
		# for performing these functions.
		if password is not None:
			u.__ = password
		if roles is not None:
			u.roles = roles
		if domains is not None:
			u.domains = domains


	def getMemberFullName(self, nameBefore=1) :
		""" Return the best full name representation """
		memberName = self.getProperty('name', default='')
		memberGivenName = self.getProperty('given_name', default='')
		memberId = self.getProperty('id', default='')
		return formatFullName(memberName, memberGivenName, memberId, nameBefore=nameBefore)

	def getMemberSortableFormat(self) :
		""" Return a specific format of full name for alphabetical sorting """
		return self.getMemberFullName(nameBefore = 1).lower()


	## overload default security declaration
	security.declareProtected(SetMemberProperties, 'setMemberProperties')
	def setMemberProperties(self, mapping):
		BaseData.setMemberProperties(self, mapping)
		self.reindexObject()

	security.declarePrivate('manage_beforeDelete')
	def manage_beforeDelete(self) :
		""" uncatalog object """
		self.unindexObject()

	def _setPortalTypeName(self, pt) :
		""" Static Dynamic Type ;-) """
		pass

	# user object interface
	# overloads to make methods not publishable
	
	def getUserName(self):
		return BaseData.getUserName(self)

	def getId(self):
		return BaseData.getId(self)

	def getRoles(self):
		return BaseData.getRoles(self)

	def getRolesInContext(self, object):
		return BaseData.getRolesInContext(self, object)

	def getDomains(self):
		return BaseData.getDomains(self)

	def has_role(self, roles, object=None):
		return BaseData.has_role(self, roles, object=None)



InitializeClass(MemberData)
