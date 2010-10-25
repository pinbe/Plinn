""" Plinn monkey patch

$Id: patch.py 1458 2009-01-30 18:11:21Z pin $
$URL: http://svn.cri.ensmp.fr/svn/Plinn/branches/CMF-2.1/patch.py $
"""
from Products.CMFCore.PortalFolder import PortalFolder as CMFPortalFolder
from Folder import PlinnFolder

CMFPortalFolder.listFolderContents = PlinnFolder.listFolderContents.im_func
CMFPortalFolder.listNearestFolderContents = PlinnFolder.listNearestFolderContents.im_func
CMFPortalFolder.listCatalogedContents = PlinnFolder.listCatalogedContents.im_func
