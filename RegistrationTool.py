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
""" Plinn registration tool: implements 3 modes to register members :
	anonymous, manager, reviewed.



"""

from Globals import InitializeClass, PersistentMapping
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFDefault.RegistrationTool import RegistrationTool as BaseRegistrationTool
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from AccessControl.Permission import Permission
from Products.CMFCore.permissions import ManagePortal, AddPortalMember
from Products.CMFCore.exceptions import AccessControl_Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.GroupUserFolder.GroupsToolPermissions import ManageGroups
from types import TupleType, ListType

security = ModuleSecurityInfo('Products.Plinn.RegistrationTool')
MODE_ANONYMOUS = 'anonymous'
security.declarePublic('MODE_ANONYMOUS')

MODE_MANAGER = 'manager'
security.declarePublic('MODE_MANAGER')

MODE_REVIEWED = 'reviewed'
security.declarePublic('MODE_REVIEWED')

MODES = [MODE_ANONYMOUS, MODE_MANAGER, MODE_REVIEWED]
security.declarePublic('MODES')

DEFAULT_MEMBER_GROUP = 'members'
security.declarePublic('DEFAULT_MEMBER_GROUP')



class RegistrationTool(BaseRegistrationTool) :

	""" Create and modify users by making calls to portal_membership.
	"""
	
	meta_type = "Plinn Registration Tool"
	
	manage_options = ({'label' : 'Registration mode', 'action' : 'manage_regmode'}, ) + \
						BaseRegistrationTool.manage_options
	
	security = ClassSecurityInfo()
	
	security.declareProtected( ManagePortal, 'manage_regmode' )
	manage_regmode = PageTemplateFile('www/configureRegistrationTool', globals(),
										__name__='manage_regmode')

	def __init__(self) :
		self._mode = MODE_ANONYMOUS
		self._chain = ''
	
	security.declareProtected(ManagePortal, 'configureTool')
	def configureTool(self, registration_mode, chain, REQUEST=None) :
		""" """
		
		if registration_mode not in MODES :
			raise ValueError, "Unknown mode: " + registration_mode
		else :
			self._mode = registration_mode
			self._updatePortalRoleMappingForMode(registration_mode)
		
		wtool = getToolByName(self, 'portal_workflow')

		if registration_mode == MODE_REVIEWED :
			if not hasattr(wtool, '_chains_by_type') :
				wtool._chains_by_type = PersistentMapping()
			wfids = []
			chain = chain.strip()
			
			if chain == '(Default)' :
				try : del wtool._chains_by_type['Member Data']
				except KeyError : pass
				self._chain = chain
			else :
				for wfid in chain.replace(',', ' ').split(' ') :
					if wfid :
						if not wtool.getWorkflowById(wfid) :
							raise ValueError, '"%s" is not a workflow ID.' % wfid
						wfids.append(wfid)
	
				wtool._chains_by_type['Member Data'] = tuple(wfids)
				self._chain = ', '.join(wfids)
		else :
			wtool._chains_by_type['Member Data'] = tuple()
		
		if REQUEST :
			REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_regmode?manage_tabs_message=Saved changes.')

	def _updatePortalRoleMappingForMode(self, mode) :
	
		urlTool = getToolByName(self, 'portal_url')
		portal = urlTool.getPortalObject()
	
		if mode in [MODE_ANONYMOUS, MODE_REVIEWED] :
			portal.manage_permission(AddPortalMember, roles = ['Anonymous', 'Manager'], acquire=1)
		elif mode == MODE_MANAGER :
			portal.manage_permission(AddPortalMember, roles = ['Manager', 'UserManager'], acquire=0)
	
	security.declarePublic('getMode')
	def getMode(self) :
		# """ return current mode """
		return self._mode[:]
	
	security.declarePublic('getWfId')
	def getWfChain(self) :
		# """ return current workflow id """
		return self._chain
	
	security.declarePublic('roleMappingMismatch')
	def roleMappingMismatch(self) :
		# """ test if the role mapping is correct for the currrent mode """
		
		mode = self._mode
		urlTool = getToolByName(self, 'portal_url')
		portal = urlTool.getPortalObject()
				
		def rolesOfAddPortalMemberPerm() :
			p=Permission(AddPortalMember, [], portal)
			return p.getRoles()
		
		if mode in [MODE_ANONYMOUS, MODE_REVIEWED] :
			if 'Anonymous' in rolesOfAddPortalMemberPerm() : return False
			
		elif mode == MODE_MANAGER :
			roles = rolesOfAddPortalMemberPerm()
			if 'Manager' in roles or 'UserManager' in roles and len(roles) == 1 and type(roles) == TupleType :
				return False
		
		return True

	security.declareProtected(AddPortalMember, 'addMember')
	def addMember(self, id, password, roles=(), groups=(DEFAULT_MEMBER_GROUP,), domains='', properties=None) :
		""" Idem CMFCore but without default role """
		BaseRegistrationTool.addMember(self, id, password, roles=roles,
									   domains=domains, properties=properties)

		if self.getMode() in [MODE_ANONYMOUS, MODE_MANAGER] :
			gtool = getToolByName(self, 'portal_groups')
			mtool = getToolByName(self, 'portal_membership')
			utool = getToolByName(self, 'portal_url')
			portal = utool.getPortalObject()
			isGrpManager = mtool.checkPermission(ManageGroups, portal) ## TODO : CMF2.1 compat
			aclu = self.aq_inner.acl_users

			for gid in groups:
				g = gtool.getGroupById(gid)
				if not isGrpManager :				
					if gid != DEFAULT_MEMBER_GROUP:
						raise AccessControl_Unauthorized, 'You are not allowed to join arbitrary group.'

				if g is None :
					gtool.addGroup(gid)
				aclu.changeUser(aclu.getGroupPrefix() +gid, roles=['Member', ])
				g = gtool.getGroupById(gid)
				g.addMember(id)


	def afterAdd(self, member, id, password, properties):
		""" notify member creation """
		member.notifyWorkflowCreated()
		member.indexObject()
		
InitializeClass(RegistrationTool)