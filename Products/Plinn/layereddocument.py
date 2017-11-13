# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.permissions import ModifyPortalContent, View
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from persistent.list import PersistentList
from zope.component.factory import Factory


class LayeredDocument(PortalContent, DefaultDublinCoreImpl) :

    """ A html document with several layers that could be edited
        separately and displayed, for instance with parallax effect.
    """

    security = ClassSecurityInfo()

    def __init__(self, id, title='', description=''):
        DefaultDublinCoreImpl.__init__(self)
        self.id = id
        self.title = title
        self.description = description
        self.setFormat('text/html')
        self.layers = PersistentList()
        self.layers.append('')



    security.declareProtected(ModifyPortalContent, 'edit')
    def edit(self, text, layer) :
        self.layers[layer] = text
        self.reindexObject()
        return True


    security.declareProtected(View, 'getLayer')
    def getLayer(self, layer) :
        return self.layers[layer]


    security.declareProtected(View, 'SearchableText')
    def SearchableText(self) :
        return '%s %s' % (super(LayeredDocument, self).SearchableText(), ' '.join([l for l in self.layers]))


InitializeClass(LayeredDocument)
LayeredDocumentFactory = Factory(LayeredDocument)
