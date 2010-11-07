""" Plinn monkey patch



"""
from Products.CMFCore.PortalFolder import PortalFolder as CMFPortalFolder
from Folder import PlinnFolder

CMFPortalFolder.listFolderContents = PlinnFolder.listFolderContents.im_func
CMFPortalFolder.listNearestFolderContents = PlinnFolder.listNearestFolderContents.im_func
CMFPortalFolder.listCatalogedContents = PlinnFolder.listCatalogedContents.im_func
