# -*- coding: utf-8 -*-
#######################################################################################
#	Plinn - http://plinn.org														  #
#	Copyright (C) 2005-2007	 Benoît PIN <benoit.pin@ensmp.fr>						  #
#																					  #
#	This program is free software; you can redistribute it and/or					  #
#	modify it under the terms of the GNU General Public License						  #
#	as published by the Free Software Foundation; either version 2					  #
#	of the License, or (at your option) any later version.							  #
#																					  #
#	This program is distributed in the hope that it will be useful,					  #
#	but WITHOUT ANY WARRANTY; without even the implied warranty of					  #
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the					  #
#	GNU General Public License for more details.									  #
#																					  #
#	You should have received a copy of the GNU General Public License				  #
#	along with this program; if not, write to the Free Software						  #
#	Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.	  #
#######################################################################################
""" Plinn implementation of CMFCore.



"""

import exceptions

from Products.CMFCore import utils as core_cmf_utils
from Products.CMFDefault import utils as default_cmf_utils
from Products.CMFCore.permissions import AddPortalContent
from Products.CMFCore.FSFile import FSFile
from Products.CMFCore.DirectoryView import registerFileExtension
import File, Folder, HugePlinnFolder, Topic
import MembershipTool
import MemberDataTool
import GroupsTool
import GroupDataTool
import RegistrationTool
import CalendarTool
import AttachmentTool

from PloneMisc import IndexIterator, Batch
import patch

from AccessControl import allow_module, allow_class


contentClasses = (File.File, Folder.PlinnFolder, HugePlinnFolder.HugePlinnFolder, Topic.Topic )

contentConstructors = (File.addFile, Folder.manage_addPlinnFolder, HugePlinnFolder.manage_addHugePlinnFolder, Topic.addTopic)

tools = ( MembershipTool.MembershipTool
		, MemberDataTool.MemberDataTool
		, GroupsTool.GroupsTool
		, GroupDataTool.GroupDataTool
		, RegistrationTool.RegistrationTool
		, CalendarTool.CalendarTool
		, AttachmentTool.AttachmentTool
		)

# register font extensions
registerFileExtension('ttf', FSFile)
registerFileExtension('eot', FSFile)

def initialize(registrar) :
	
	allow_module('quopri')
	allow_module('Products.Plinn.PloneMisc')
	allow_class(IndexIterator)
	allow_class(Batch)
	
	core_cmf_utils.ContentInit(
	'Plinn',
	content_types = contentClasses,
	permission = AddPortalContent,
	extra_constructors = contentConstructors,
	).initialize(registrar)
	
	core_cmf_utils.ToolInit('Plinn Tool',
					tools = tools,
					icon = 'tool.gif'
					).initialize(registrar)
	
	


# Monkey...
# all tags are good !
validTags = default_cmf_utils.NASTY_TAGS.copy()
for tag in validTags.keys() :
	validTags[tag] = 1

VALID_TAGS = {'font': 1, 'param' : 1, 'iframe' : 1}

validTags.update(VALID_TAGS)

default_cmf_utils.NASTY_TAGS = {}
default_cmf_utils.VALID_TAGS.update(validTags)

# the plinn portal_calendar is a also a "SPECIAL PROVIDER"
# TODO: vérifier l'impact
# import Products.CMFCore.exportimport.actions
# Products.CMFCore.exportimport.actions._SPECIAL_PROVIDERS += ('portal_calendar',)


# monkey-patch de getIcon qui est foirasse dans CMF2.2 : 
# les icônes ne s'affichent pas correctement dans la ZMI
# lorqu'on y accède par un virtual host apache.
from urllib import quote
from Products.CMFCore.utils import getToolByName

def getIcon(self, relative_to_portal=0):
	"""
	Using this method allows the content class
	creator to grab icons on the fly instead of using a fixed
	attribute on the class.
	"""
	ti = self.getTypeInfo()
	if ti is not None:
		icon = quote(ti.getIcon())
		if icon:
			if relative_to_portal:
				return icon
			else:
				# Relative to REQUEST['BASEPATH1']
				portal_url = getToolByName( self, 'portal_url' )
				res = portal_url(relative=1) + '/' + icon
				while res[:1] == '/':
					res = res[1:]
				return res
	return 'misc_/OFSP/dtmldoc.gif'

icon = getIcon	# For the ZMI

from Products.CMFCore.DynamicType import DynamicType
DynamicType.getIcon = getIcon
DynamicType.icon = getIcon
