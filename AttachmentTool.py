# -*- coding: utf-8 -*-
#######################################################################################
#   Plinn - http://plinn.org                                                          #
#   © 2007-2014  Benoît Pin <pin@cri.ensmp.fr>                                        #
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
""" Portal attachment management tool.



"""

from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from OFS.Image import File, cookId
from zExceptions import Unauthorized
from zExceptions import BadRequest
from Products.Photo import Photo
from Products.CMFCore.utils import UniqueObject, getToolByName, getUtilityByInterfaceName
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFCore.exceptions import AccessControl_Unauthorized
from Products.Plinn.utils import makeValidId

from urllib import unquote
from cgi import escape
from ZServer import LARGE_FILE_THRESHOLD
from webdav.interfaces import IWriteLock
from webdav.common import Locked
from webdav.common import PreconditionFailed
from zope.contenttype import guess_content_type



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
            thumbSize = {'thumb_height' : portal.getProperty('thumb_size', 192),
                         'thumb_width'  : portal.getProperty('thumb_size', 192)}
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

    security.declarePrivate('checkIdAvailable')
    def checkIdAvailable(self, id):
        try:
            self._checkId(id)
        except BadRequest:
            return False
        else:
            return True


    security.declareProtected(ModifyPortalContent, 'put_upload')
    def put_upload(self, REQUEST, RESPONSE):
        """ Upload a content thru webdav put method.
            The default behavior (NullRessource.PUT + PortalFolder.PUT_factory)
            disallow files names with '_' at the begining.
        """

        self.dav__init(REQUEST, RESPONSE)
        fileName = unquote(REQUEST.getHeader('X-File-Name', ''))
        validId = makeValidId(self, fileName, allow_dup=True)

        ifhdr = REQUEST.get_header('If', '')
        if self.wl_isLocked():
            if ifhdr:
                self.dav__simpleifhandler(REQUEST, RESPONSE, col=1)
            else:
                raise Locked
        elif ifhdr:
            raise PreconditionFailed

        if int(REQUEST.get('CONTENT_LENGTH') or 0) > LARGE_FILE_THRESHOLD:
            file = REQUEST['BODYFILE']
            body = file.read(LARGE_FILE_THRESHOLD)
            file.seek(0)
        else:
            body = REQUEST.get('BODY', '')

        typ=REQUEST.get_header('content-type', None)
        if typ is None:
            typ, enc=guess_content_type(validId, body)

        if self.checkIdAvailable(validId) :
            if typ.startswith('image/') :
                utool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IURLTool')
                portal = utool.getPortalObject()
                thumbSize = {'thumb_height' : portal.getProperty('thumb_size', 192),
                             'thumb_width'  : portal.getProperty('thumb_size', 192)}
                ob = Photo(validId, fileName, '', **thumbSize)
            else :
                ob = File(validId, fileName, '')
            
            self._setObject(validId, ob)
            httpRespCode = 201
        else :
            httpRespCode = 200
            ob = self._getOb(validId)

        # We call _verifyObjectPaste with verify_src=0, to see if the
        # user can create this type of object (and we don't need to
        # check the clipboard.
        try:
            self._verifyObjectPaste(ob.__of__(self), 0)
        except CopyError:
             sMsg = 'Unable to create object of class %s in %s: %s' % \
                    (ob.__class__, repr(self), sys.exc_info()[1],)
             raise Unauthorized, sMsg

        ob.PUT(REQUEST, RESPONSE)
        RESPONSE.setStatus(httpRespCode)
        RESPONSE.setHeader('Content-Type', 'text/xml;;charset=utf-8')
        if ob.meta_type == 'File' :
            return '<element id="%s" title="%s"/>' % (ob.getId(), escape(ob.title_or_id()))
        elif ob.meta_type == 'Photo' :
            width, height = ob.getResizedImageSize(size=(310, 310))
            return '<element src="%(src)s" title="%(title)s" width="%(width)d" height="%(height)d"/>' % \
                {'src' : 'attachments/%s/getResizedImage?size=%d_%d' % (ob.getId(), width, height),
                 'title' : escape(ob.title_or_id()),
                 'width' : width,
                 'height' : height
                 }


InitializeClass(AttachmentContainer)