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
        if layer > 128:
            raise ValueError, 'Layer number could not exeed 128'

        if layer > len(self.layers) - 1 :
            for i in range(layer - (len(self.layers) - 1)):
                self.layers.append('')

        self.layers[layer] = text
        self.reindexObject()
        return True

    security.declareProtected(View, 'getLayer')
    def getLayer(self, layer) :
        try :
            return self.layers[layer]
        except IndexError :
            return ''

    security.declareProtected(View, 'getLayerLength')
    def getLayerLength(self) :
        return max(len(self.layers), 2)

    security.declareProtected(ModifyPortalContent, 'layersStack')
    def layersStack(self) :
        return ''.join([('<div>%s</div>' % l) for l in self.layers])

    security.declareProtected(View, 'SearchableText')
    def SearchableText(self) :
        return '%s %s' % (super(LayeredDocument, self).SearchableText(), ' '.join([l for l in self.layers]))


InitializeClass(LayeredDocument)
LayeredDocumentFactory = Factory(LayeredDocument)
