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
""" This module implements a portal-managed File class that's inherits of CMFDefault
	File. If exists, portal_transforms is called to extract text content, and publish
	attachments.



"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
import OFS
from zope.component.factory import Factory

from Products.CMFDefault.File import File as BaseFile
from Products.CMFCore.permissions import View, ModifyPortalContent
from Products.CMFCore.utils import getToolByName
from hexagonit.swfheader import parse as parseswf

class File(BaseFile) :
	""" file class with portal_transforms support """
	
	security = ClassSecurityInfo()
	
	_properties = BaseFile._properties + ({'id':'orig_name', 'type':'string', 'mode':'w', 'label':"Original Name"},)
	orig_name = ''


	def __getattr__(self, name) :
		try : return BaseFile.__getattr__(self, name)
		except :
			selfAttrs = self.__dict__
			if selfAttrs.has_key('_v_transform_cache') :
				cache = selfAttrs['_v_transform_cache']
				cacheTuple = cache.get('text_html', None) # (time, value)
				if cacheTuple :
					cacheData = cacheTuple[1]
				
					subObDict = cacheData.getSubObjects()
					if subObDict.has_key(name) :
						fileOb = OFS.Image.File(name, name, subObDict[name])
						return fileOb
				
			raise AttributeError, name
	
	def manage_upload(self,file='',REQUEST=None):
		ret = super(File, self).manage_upload(file=file, REQUEST=REQUEST)

		orig_name = OFS.Image.cookId('', '', file)[0]
		if orig_name :
			self.orig_name = orig_name

		print self.absolute_url(), self.Format()
		if self.Format() == 'application/x-shockwave-flash' :
			if file :
				try :
					swfmetadata = parseswf(file)
				except IOError :
					swfmetadata = {'width':600, 'height':600}

			for name in ('width', 'height') :
				value = swfmetadata[name]
				if self.hasProperty(name) :
					self._updateProperty(name, value)
				else :
					self.manage_addProperty(name, value, 'int')
		self.reindexObject()
		return ret
		
		
	
	security.declareProtected(ModifyPortalContent, 'edit')
	def edit(self, precondition='', file=''):
		orig_name = OFS.Image.cookId('', '', file)[0]
		if orig_name :
			self.orig_name = orig_name
		BaseFile.edit(self, precondition=precondition, file=file)
		if hasattr(self, '_v_transform_cache') :
			del self._v_transform_cache
	
	
	security.declareProtected(View, 'SearchableText')
	def SearchableText(self) :
		""" Return full text"""
		baseSearchableText = BaseFile.SearchableText(self)
		transformTool = getToolByName(self, 'portal_transforms', default=None)
		if transformTool is None :
			return baseSearchableText
		else :
			datastream_text =  transformTool.convertTo('text/plain',
														str(self.data),
														mimetype = self.content_type
														)
			full_text = ''
			if datastream_text is not None :
				full_text = datastream_text.getData()
			
			return baseSearchableText + full_text
			
	security.declareProtected(View, 'preview')
	def preview(self) :
		"""Return HTML preview if it's possible or empty string """
		transformTool = getToolByName(self, 'portal_transforms', default = None)
		if transformTool is None :
			return ''
		else :
			filename = self.getId().replace(' ', '_')
			datastream = transformTool.convertTo('text/html',
												str(self.data),
												object=self,
												mimetype = self.content_type,
												filename = filename)

			if datastream is not None : return datastream.getData()
			else : return ''

	security.declareProtected(View, 'download')
	def download(self, REQUEST, RESPONSE):
		"""Download this item.
		
		Calls OFS.Image.File.index_html to perform the actual transfer after
		first setting Content-Disposition to suggest a filename.
		
		This method is deprecated, use the URL of this object itself. Because
		the default view of a File object is to download, rather than view,
		this method is obsolete. Also note that certain browsers do not deal
		well with a Content-Disposition header.

		"""

		RESPONSE.setHeader('Content-Disposition',
						   'attachment; filename=%s' % (self.orig_name or self.getId()))
		return OFS.Image.File.index_html(self, REQUEST, RESPONSE)
	
	security.declarePublic('getIcon')
	def getIcon(self, relative_to_portal=0):
		""" return icon corresponding to mime-type
		"""
		regTool = getToolByName(self, 'mimetypes_registry', default=None)
		if regTool :
			mime = regTool(str(self.data), mimetype=self.content_type)[2]
			return mime.icon_path
		else :
			return BaseFile.getIcon(self, relative_to_portal=relative_to_portal)


InitializeClass(File)
FileFactory = Factory(File)


def addFile( dispatcher
			 , id
			 , title=''
			 , file=''
			 , content_type=''
			 , precondition=''
			 , subject=()
			 , description=''
			 , contributors=()
			 , effective_date=None
			 , expiration_date=None
			 , format='text/html'
			 , language=''
			 , rights=''
			 ):
	"""
	Add a File
	"""

	# cookId sets the id and title if they are not explicity specified
	id, title = OFS.Image.cookId(id, title, file)

	container = dispatcher.Destination()

	# Instantiate the object and set its description.
	fobj = File( id, title=title, file='', content_type=content_type,
				 precondition=precondition, subject=subject, description=description,
				 contributors=contributors, effective_date=effective_date,
				 expiration_date=expiration_date, format=format,
				 language=language, rights=rights
				  )
	
	# Add the File instance to self
	container._setObject(id, fobj)

	# 'Upload' the file.  This is done now rather than in the
	# constructor because the object is now in the ZODB and
	# can span ZODB objects.
	container._getOb(id).manage_upload(file)