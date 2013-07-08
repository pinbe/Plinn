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
""" Plinn portal_membership



"""

from AccessControl import ClassSecurityInfo, getSecurityManager
from AccessControl.unauthorized import Unauthorized
from AccessControl.SpecialUsers import nobody
from AccessControl.Permission import Permission
from Acquisition import aq_base, aq_inner
from Globals import InitializeClass, MessageDialog
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

from Products.CMFDefault.MembershipTool import MembershipTool as BaseTool
from Products.CMFCore.permissions import View, ListPortalMembers, ManagePortal, SetOwnPassword, ChangePermissions
from permissions import RemoveMember, SetLocalRoles, CheckMemberPermission
from utils import _checkMemberPermission
from Products.CMFCore.utils import getToolByName, _checkPermission, _getAuthenticatedUser
from utils import formatFullName, translate
from Products.CMFDefault.utils import decode
from Products.CMFDefault.Document import addDocument

from sets import Set
from types import TupleType


from time import time
from logging import getLogger
console = getLogger('Plinn.MembershipTool')


class MembershipTool( BaseTool ):
	""" Implement 'portal_membership' interface using "stock" policies.
	"""


	meta_type = 'Plinn Membership Tool'
	
	manage_options=( ({ 'label' : 'Configuration'
						, 'action' : 'manage_mapRoles'
						 },) + BaseTool.manage_options[1:])

	security = ClassSecurityInfo()
	
	security.declareProtected(ManagePortal, 'manage_mapRoles')
	manage_mapRoles = PageTemplateFile('www/configureMembershipTool', globals(),
								   __name__='manage_mapRoles')

	#
	#	'portal_membership' interface methods
	#

	# change security settings for inherited methods
	security.declareProtected(ListPortalMembers, 'getMemberById')
	
	
	memberareaPortalType = 'Huge Plinn Folder'
	

#	security.declareProtected(SetOwnPassword, 'setPassword')
#	def setPassword(self, password, domains=None):
#		'''Allows the authenticated member to set his/her own password.
#		'''
#		user_folder = self.__getPUS()
#		if user_folder.meta_type == 'Group User Folder' :
#			registration = getToolByName(self, 'portal_registration', None)
#			if not self.isAnonymousUser():
#				member = self.getAuthenticatedMember()
#				if registration:
#					failMessage = registration.testPasswordValidity(password)
#					if failMessage is not None:
#						raise 'Bad Request', failMessage
#				member.setSecurityProfile(password=password, domains=domains)
#				member.changePassword(password)
#			else:
#				raise 'Bad Request', 'Not logged in.'
#			
#		else :
#			BaseTool.setPassword(self, password, domains=None)



	security.declareProtected(ListPortalMembers, 'listMemberIds')
	def listMemberIds(self):
		'''Lists the ids of all members.	This may eventually be
		replaced with a set of methods for querying pieces of the
		list rather than the entire list at once.
		'''
		user_folder = self.__getPUS()
		if user_folder.meta_type == 'Group User Folder' :
			return user_folder.getPureUserNames()
		else :
			return [ x.getId() for x in user_folder.getUsers() ]
			
	
	security.declareProtected(CheckMemberPermission, 'checkMemberPermission')
	def checkMemberPermission(self, userid, permissionName, object, subobjectName=None):
		'''
		Checks whether the current user has the given permission on
		the given object or subobject.
		'''
		if subobjectName is not None:
			object = getattr(object, subobjectName)
		
		return _checkMemberPermission(userid, permissionName, object)
	
	security.declareProtected(ListPortalMembers, 'listMembers')
	def listMembers(self):
		'''Gets the list of all members.
		'''
		user_folder = self.__getPUS()
		if user_folder.meta_type == 'Group User Folder' :
			return map(self.wrapUser, user_folder.getPureUsers())
		else :
			return map(self.wrapUser, user_folder.getUsers())

	
	security.declareProtected(View, 'getCandidateLocalRoles')
	def getCandidateLocalRoles(self, obj) :
		""" What local roles can I assign?
		"""
		member = self.getAuthenticatedMember()
		valid_roles = obj.valid_roles()
		if 'Manager' in member.getRoles():
			local_roles = [r for r in valid_roles if r != 'Anonymous']
		else:
			sm = getSecurityManager()
			allPermissions = self.ac_inherited_permissions(1)

			# construct a dictionary of permissions indexed by role
			# and get permissions of user in obj context
			memberPermissions = Set()
			rolesMappings = {}
			for role in valid_roles :
				rolesMappings[role] = Set()

			for p in allPermissions:
				name, value = p[:2]

				p=Permission(name,value,obj)
				rolesOfPerm = p.getRoles()

				for role in rolesOfPerm :
					try : rolesMappings[role].add(name)
					except KeyError :
						trName = p._p
						if hasattr(obj, trName):
							l = list(getattr(obj, trName))
							l.remove(role)
							setattr(obj, trName, tuple(l))
							msg = '%s role has been removed for %s permission on %s ' % (role, name, obj.absolute_url())
							#LOG('portal_membership', WARNING, msg)

				parent = obj.aq_inner.aq_parent
				while type(rolesOfPerm) != TupleType :
					p=Permission(name, value, parent)
					rolesOfPerm = p.getRoles()
					for role in rolesOfPerm :
						try : rolesMappings[role].add(name)
						except KeyError : pass
					try : parent = parent.aq_inner.aq_parent
					except AttributeError : break
					

				if sm.checkPermission(name, obj) :
					memberPermissions.add(name)

			local_roles = []
			for role in valid_roles :
				if rolesMappings[role] and rolesMappings[role].issubset(memberPermissions) :
					local_roles.append(role)
			
		local_roles = [ role for role in local_roles if role not in ('Shared', 'Authenticated', 'Member', 'Anonymous') ]
		local_roles.sort()
		return tuple(local_roles)
	
	
	security.declareProtected(View, 'setLocalRoles')
	def setLocalRoles( self, obj, member_ids, role, remove=0, reindex=1 ):
		""" Set local roles on an item """
		if role not in self.getCandidateLocalRoles(obj) :
			raise Unauthorized, "You are not allowed to manage %s role" % role

		if self.checkPermission(SetLocalRoles, obj) :
			if not remove :
				for member_id in member_ids :
					# current roles for user id in obj
					roles = list(obj.get_local_roles_for_userid( userid=member_id ))
					if role not in roles :
						roles.append(role)
						obj.manage_setLocalRoles( member_id, roles)
			else :
				for member_id in member_ids :
					# current roles for user id in obj
					roles = list(obj.get_local_roles_for_userid( userid=member_id ))
					try : roles.remove(role)
					except ValueError : pass
					else :
						if len(roles) >= 1 :
							obj.manage_setLocalRoles( member_id, roles)
						else :
							obj.manage_delLocalRoles( userids=[member_id] )
							
		else :
			raise Unauthorized
				
		if reindex:
			# It is assumed that all objects have the method
			# reindexObjectSecurity, which is in CMFCatalogAware and
			# thus PortalContent and PortalFolder.
			obj.reindexObjectSecurity()

	
	security.declarePublic('getMemberFullNameById')
	def getMemberFullNameById(self, userid, nameBefore = 1) :
		""" Return	the best formated representation of user fullname. """
		
		memberFullName = ''
		if userid and userid != 'No owner' :
			# No owner is a possible value returned by DefaultDublinCoreImpl.Creator
			member = self.getMemberById(userid)
			if not member :
				return userid
			memberName = getattr(member, 'name', '')
			memberGivenName = getattr(member, 'given_name', '')
			memberId = member.getId()
			memberFullName = formatFullName(memberName, memberGivenName, memberId, nameBefore = nameBefore)
			
		return memberFullName
	
	security.declareProtected(ListPortalMembers, 'getMembers')
	def getMembers(self, users) :
		""" Return wraped users """
		members = []
		for user in users :
			members.append(self.getMemberById(user))
		
		members = filter(None, members)
		members.sort( lambda m0, m1 : cmp(m0.getMemberSortableFormat(), m1.getMemberSortableFormat()) )
		return members
	

	security.declareProtected(ListPortalMembers, 'getOtherMembers')
	def getOtherMembers(self, users) :
		""" Return members who are not in users list"""
		allMemberIds = self.listMemberIds()
		otherMemberIds = [ userId for userId in allMemberIds if userId not in users ]
		return self.getMembers(otherMemberIds)



	security.declareProtected(ListPortalMembers, 'getMembersMetadata')
	def getMembersMetadata(self, users) :
		""" return metadatas from portal_catalog """
		userDict = {}
		for u in users : userDict[u] = True
		ctool = getToolByName(self, 'portal_catalog')
		memberBrains = ctool(portal_type='Member Data', sort_on='getMemberSortableFormat')
		memberList = []
		complementList = []
		
		if users :
			for mb in memberBrains :
				metadatas = {'id' : mb.getId, 'fullname' : mb.getMemberFullName}
				if userDict.has_key(mb.getId) :
					memberList.append(metadatas)
				else :
					complementList.append(metadatas)
		else :
			complementList = [{'id' : mb.getId, 'fullname' : mb.getMemberFullName} for mb in memberBrains]

		return {'memberList' : memberList, 'complementList' : complementList}
		
			
	
	security.declareProtected(RemoveMember, 'removeMembers')
	def removeMembers(self, memberIds = []) :
		""" remove member
		"""
		# TODO : remove member document ?
		mdtool = getToolByName(self, 'portal_memberdata')
		for m in self.getMembers(memberIds) :
			m.manage_beforeDelete()
			mdtool.deleteMemberData(m.getId())

		self.aq_inner.acl_users.deleteUsers(users = memberIds)



	security.declareProtected(ManagePortal, 'setMemberAreaPortalType')
	def setMemberAreaPortalType(self, member_folder_portal_type):
		""" Set member area portal type to construct."""
		ttool = getToolByName(self, 'portal_types')
		if member_folder_portal_type not in ttool.objectIds() :
			raise ValueError, "Unknown portal type : %s" % str(member_folder_portal_type)
		
		self.memberareaPortalType = member_folder_portal_type
		return MessageDialog(title  ='Type updated',
							 message='The member area type have been updated',
							 action ='manage_mapRoles')
	
	def getMemberAreaPortalType(self) :
		return self.memberareaPortalType


	def getHomeFolder(self, id=None, verifyPermission=0):
		""" Return a member's home folder object, or None.
		"""
		if id is None:
			member = self.getAuthenticatedMember()
			if not hasattr(member, 'getMemberId'):
				return None
			id = member.getMemberId()
		members = self.getMembersFolder()
		if members is not None:
			if not hasattr(members, id) and getattr(self, 'memberareaCreationFlag', 0) != 0 :
				self.createMemberArea(id)
			try:
				folder = members._getOb(id)
				if verifyPermission and not _checkPermission(View, folder):
					# Don't return the folder if the user can't get to it.
					return None
				return folder
			except (AttributeError, TypeError, KeyError):
				pass
		return None

	security.declarePublic('createMemberArea')
	def createMemberArea(self, member_id=''):
		""" Create a member area for 'member_id' or authenticated user.
		"""
		if not self.getMemberareaCreationFlag():
			return None
		members = self.getMembersFolder()
		if not members:
			return None
		if self.isAnonymousUser():
			return None
		# Note: We can't use getAuthenticatedMember() and getMemberById()
		# because they might be wrapped by MemberDataTool.
		user = _getAuthenticatedUser(self)
		user_id = user.getId()
		if member_id in ('', user_id):
			member = user
			member_id = user_id
		else:
			if _checkPermission(ManageUsers, self):
				member = self.acl_users.getUserById(member_id, None)
				if member:
					member = member.__of__(self.acl_users)
				else:
					raise ValueError, 'Member %s does not exist' % member_id
			else:
				return None
		
		if hasattr( aq_base(members), member_id ):
			return None
			
		ttool = getToolByName(self, 'portal_types')
		info = getattr(ttool, self.memberareaPortalType)
		
		memberFullName = self.getMemberFullNameById(member_id, nameBefore = 0)
		f = info._constructInstance( members, member_id, title=memberFullName )
		
		# Grant Ownership and Owner role to Member
		f.changeOwnership(user)
		f.__ac_local_roles__ = None
		f.manage_setLocalRoles(member_id, ['Owner'])

		f.reindexObjectSecurity()
		
		# Create Member's initial content.
		if hasattr(self, 'createMemberContent') :
			self.createMemberContent(member=user,
									 member_id=member_id,
									 member_folder=f)
		else :
			def _(message, context, expand=()) :
				trmessage = decode(translate(message, context), context)
				expand = tuple([decode(e, context) for e in expand])
				return (trmessage % expand).encode('utf-8')
						
			# Create Member's home page.
			addDocument( f
						, 'index_html'
						, title = _("%s's Home", self, (memberFullName,))
						, description = _("%s's front page", self, (memberFullName,))
						, text_format = "html"
						, text = self.default_member_content(memberFullName=memberFullName).encode('utf-8')
						)
	
			# Grant Ownership and Owner role to Member
			f.index_html.changeOwnership(user)
			f.index_html.__ac_local_roles__ = None
			f.index_html.manage_setLocalRoles(member_id, ['Owner'])
	
			f.index_html._setPortalTypeName( 'Document' )
	
			# Overcome an apparent catalog bug.
			f.index_html.reindexObject()
			wftool = getToolByName( f, 'portal_workflow' )
			wftool.notifyCreated( f.index_html )
		
		return f
	

	security.declareProtected(ListPortalMembers, 'looseSearchMembers')
	def looseSearchMembers(self, searchString) :
		""" """
		
		words = searchString.strip().split()
		words = [word.lower() for word in words]
		
		mdtool = getToolByName(self, 'portal_memberdata')
		mdProperties = mdtool.propertyIds()
		searchableProperties = [ p['id'] for p in mdtool.propertyMap() if p['type'] == 'string' ] + ['id']
		try : searchableProperties.remove('portal_skin')
		except ValueError : pass
		
		match = []
		for m in self.listMembers() :
			allWordsMatch = False
			for word in words :
				for p in searchableProperties :
					if str(m.getProperty(p, '')).lower().find(word) != -1 :
						allWordsMatch = True
						break
				else :
					allWordsMatch = False
					
				if not allWordsMatch :
					break
			else :
				match.append(m)
		
		return match

	def __getPUS(self):
		# CMFCore.MembershipTool.MembershipTool tests 'getUsers' method but :
		# "enumeration" methods ('getUserNames', 'getUsers') are *not*
		# part of the contract!  See IEnumerableUserFolder.
		# (from PluggableAuthService.interfaces.authservice #233)
		return self.acl_users

		
InitializeClass(MembershipTool)
