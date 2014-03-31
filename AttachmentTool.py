# -*- coding: utf-8 -*-
#######################################################################################
#	Plinn - http://plinn.org														  #
#	Copyright (C) 2007	Benoît PIN <benoit.pin@ensmp.fr>							  #
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
""" Basic portal attachment management tool.



"""

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from OFS.Image import File, cookId
from Products.Photo import Photo
from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.exceptions import AccessControl_Unauthorized
from Products.Plinn.utils import makeValidId


class AttachmentTool( UniqueObject, SimpleItem):
	""" Links attachment objects to contents.
	"""

	id = 'portal_attachment'
	meta_type = 'Attachment Tool'
	manage_options = SimpleItem.manage_options

	security = ClassSecurityInfo()

	security.declarePublic('getAttachmentsFor')
	def getAttachmentsFor(self, content):
		"""getAttachmentsFor returns attachments container of content
		"""
		if getattr( aq_base(content), 'attachments', None ) is None :
			self._createAttachmentContainerFor(content)
		
		return content.attachments
	
	security.declarePrivate('_createAttachmentContainerFor')
	def _createAttachmentContainerFor(self, content):
		"""_createAttachmentContainerFor documentation
		"""
		
		content.attachments = AttachmentContainer()
	
	security.declarePublic('uploadAttachmentFor')
	def uploadAttachmentFor(self, content, file, title='', typeName='File') :
		"upload attachment inside content's attachment folder."
		
		mtool = getToolByName(self, 'portal_membership')
		if not mtool.checkPermission(ModifyPortalContent, content) :
			raise AccessControl_Unauthorized
		
		utool = getToolByName(self, 'portal_url')
		portal = utool.getPortalObject()
		
		attachments = self.getAttachmentsFor(content)
		dummy, title = cookId('', title, file)
		id = makeValidId(attachments, title)
		
		if typeName == 'Photo':
			thumbSize = {'thumb_height'	: portal.getProperty('thumb_size', 128),
						 'thumb_width'	: portal.getProperty('thumb_size', 128)}
			fileOb = Photo(id, title, file, **thumbSize)
		elif typeName == 'File' :
			fileOb = File(id, title, '')
			fileOb.manage_upload(file)
		else :
			raise AccessControl_Unauthorized

		content.attachments._setObject(id, fileOb)
		fileOb = getattr(content.attachments, id)
		return fileOb
		
		

InitializeClass( AttachmentTool )


class AttachmentContainer (Folder):
	
	meta_type = 'Attachment container'
	security = ClassSecurityInfo()
	
	def __init__(self):
		self.id = 'attachments'

InitializeClass(AttachmentContainer)