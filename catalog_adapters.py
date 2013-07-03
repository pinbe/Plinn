from Products.CMFCore.CatalogTool import IndexableObjectWrapper

class PlinnIndexableObjectWrapper(IndexableObjectWrapper) :
    def position(self) :
        parent = self.getParentNode()
        pos = parent.getObjectPosition(self.getId())
        return pos