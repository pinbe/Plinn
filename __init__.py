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
""" Plinn implementation of CMFCore.

$Id: __init__.py 1530 2009-07-08 09:19:39Z pin $
$URL: http://svn.cri.ensmp.fr/svn/Plinn/branches/CMF-2.1/__init__.py $
"""

import exceptions

from Products.CMFCore import utils as core_cmf_utils
from Products.CMFDefault import utils as default_cmf_utils
from Products.CMFCore.permissions import AddPortalContent
import File, Folder, HugePlinnFolder, Topic
import MembershipTool
import MemberDataTool
import GroupsTool
import GroupDataTool
import RegistrationTool
import CalendarTool
import AttachmentTool
#from shutdown_dispatcher import ZopeShutdownDispatcher

from PloneMisc import IndexIterator, Batch
from utils import  getCPInfo, popCP

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

methods = {
'getCPInfo': getCPInfo,
'getCPInfo__roles__': None,
'popCP' : popCP,
'popCP__roles__' : None
}

def initialize(registrar) :
	
	allow_module('quopri')
	allow_module('Products.Plinn.PloneMisc')
	allow_class(IndexIterator)
	allow_class(Batch)
	app = registrar._ProductContext__app
	#ZopeShutdownDispatcher(registrar._ProductContext__app)
	
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

VALID_TAGS = {'font': 1}

validTags.update(VALID_TAGS)

default_cmf_utils.NASTY_TAGS = {}
default_cmf_utils.VALID_TAGS.update(validTags)

# TODO : vérifier l'impact.
# # the plinn portal_calendar is a also a "SPECIAL PROVIDER"
# import Products.CMFCore.exportimport.actions
# Products.CMFCore.exportimport.actions._SPECIAL_PROVIDERS += ('portal_calendar',)
