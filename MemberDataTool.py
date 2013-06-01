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



"""
from AccessControl.interfaces import IUser
from Products.CMFCore.interfaces import IMemberDataTool
from Globals import InitializeClass
from Acquisition import aq_inner, aq_parent, aq_base
from AccessControl import ClassSecurityInfo
from OFS.SimpleItem import SimpleItem
from Products.CMFCore.MemberDataTool import MemberDataTool as BaseTool
from Products.CMFCore.MemberDataTool import MemberData as BaseData
from Products.CMFCore.MemberDataTool import MemberAdapter as BaseMemberAdapter
from zope.component import adapts
from zope.interface import implements
from Products.CMFCore.interfaces import IMember
# from Products.CMFCore.MemberDataTool import CleanupTemp
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
	
	def wrapUser(self, u) :
	    wu = super(MemberDataTool, self).wrapUser(u)
	    return wu.__of__(self).__of__(u)
    

	def __bobo_traverse__(self, REQUEST, name):
		if hasattr(self,name):
			return getattr(self,name)
		else:
			if self._members.has_key(name) :
				return self.wrapUser(self.acl_users.getUser(name))

InitializeClass(MemberDataTool)


class MemberAdapter(BaseMemberAdapter, SimpleItem, DynamicType, CMFCatalogAware):

	"""Member data adapter.
	"""

	adapts(IUser, IMemberDataTool)
	implements(IMember)
	
	portal_type = 'Member Data'

	security = ClassSecurityInfo()
	
	def __init__(self, user, tool):
		super(MemberAdapter, self).__init__(user, tool)
		self.id = self.getId()

	security.declarePublic('getMemberFullName')
	def getMemberFullName(self, nameBefore=1) :
		""" Return the best full name representation """
		memberName = self.getProperty('name', default='')
		memberGivenName = self.getProperty('given_name', default='')
		memberId = self.getId()
		return formatFullName(memberName, memberGivenName, memberId, nameBefore=nameBefore)

	def getMemberSortableFormat(self) :
		""" Return a specific format of full name for alphabetical sorting """
		return self.getMemberFullName(nameBefore = 1).lower()
	
	# security overload
	security.declareProtected(SetMemberProperties, 'setMemberProperties')
	def setMemberProperties(self, mapping):
		super(MemberAdapter, self).setMemberProperties(mapping)
		self.reindexObject()
    

InitializeClass(MemberAdapter)


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

# migré
#	def getMemberFullName(self, nameBefore=1) :
#		""" Return the best full name representation """
#		memberName = self.getProperty('name', default='')
#		memberGivenName = self.getProperty('given_name', default='')
#		memberId = self.getProperty('id', default='')
#		return formatFullName(memberName, memberGivenName, memberId, nameBefore=nameBefore)

# migré
#	def getMemberSortableFormat(self) :
#		""" Return a specific format of full name for alphabetical sorting """
#		return self.getMemberFullName(nameBefore = 1).lower()


# migré
#	## overload default security declaration
#	security.declareProtected(SetMemberProperties, 'setMemberProperties')
#	def setMemberProperties(self, mapping):
#		BaseData.setMemberProperties(self, mapping)
#		self.reindexObject()

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
