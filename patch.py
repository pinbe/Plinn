""" Plinn monkey patch



"""
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ListFolderContents, View, ViewManagementScreens,\
                                         ManageProperties, AddPortalFolders, AddPortalContent,\
                                         ManagePortal, ModifyPortalContent

from Products.CMFCore.PortalFolder import PortalFolder as CMFPortalFolder
from Folder import PlinnFolder

cmfPortalFolderSecurity = ClassSecurityInfo()

cmfPortalFolderSecurity.declareProtected(ListFolderContents, 'listFolderContents')
CMFPortalFolder.listFolderContents = PlinnFolder.listFolderContents.im_func

cmfPortalFolderSecurity.declareProtected(ListFolderContents, 'listNearestFolderContents')
CMFPortalFolder.listNearestFolderContents = PlinnFolder.listNearestFolderContents.im_func

cmfPortalFolderSecurity.declareProtected(ListFolderContents, 'listCatalogedContents')
CMFPortalFolder.listCatalogedContents = PlinnFolder.listCatalogedContents.im_func

cmfPortalFolderSecurity.declareProtected(AddPortalContent, 'put_upload')
CMFPortalFolder.put_upload = PlinnFolder.put_upload.im_func

cmfPortalFolderSecurity.apply(CMFPortalFolder)


from Products.CMFDefault.formlib.form import _EditFormMixin
from patch_impl import _setRedirect
_EditFormMixin._setRedirect = _setRedirect