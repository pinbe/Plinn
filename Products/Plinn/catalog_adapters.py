from Products.CMFCore.CatalogTool import IndexableObjectWrapper
from OFS.interfaces import IOrderedContainer

class PlinnIndexableObjectWrapper(IndexableObjectWrapper) :
    def position(self) :
        parent = self.getParentNode()
        if IOrderedContainer.providedBy(parent) :
            pos = parent.getObjectPosition(self.getId())
            return pos