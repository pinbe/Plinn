# -*- coding: utf-8 -*-
from App.class_init import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.interfaces import IIndexableObject
from Products.CMFCore.CatalogTool import CatalogTool as BaseCatalogTool
from Products.CMFCore.CatalogTool import IndexableObjectWrapper
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.permissions import ModifyPortalContent
from zope.component import queryMultiAdapter
from Products.ZCatalog.Catalog import Catalog
import transaction
from solr import *

class SolrTransactionHook :
    ''' commit solr couplé sur le commit de la ZODB '''
    def __init__(self, connection) :
        self.connection = connection
    
    def __call__(self, status) :
        if status :
            self.connection.commit()
            self.connection.close()
        else :
            self.connection.close()

class CatalogTool(BaseCatalogTool) :
    meta_type = 'Legivoc Catalog'
    security = ClassSecurityInfo()
    manage_options = (BaseCatalogTool.manage_options[:5] +
                      ({'label' : 'Solr', 'action' : 'manage_solr'},) +
                      BaseCatalogTool.manage_options[5:])
    manage_solr = PageTemplateFile('www/manage_solr', globals())
    
    
    def __init__(self, idxs=[]) :
        super(CatalogTool, self).__init__()
        self._catalog = DelegatedCatalog()
        self.solr_url = 'http://localhost:8983/solr'
        self.delegatedIndexes = ('Title', 'Description', 'SearchableText')
    
    security.declarePrivate('solrAdd')
    def solrAdd(self, object, idxs=[], uid=None) :
        if IIndexableObject.providedBy(object):
            w = object
        else:
            w = queryMultiAdapter( (object, self), IIndexableObject )
            if w is None:
                # BBB
                w = IndexableObjectWrapper(object, self)
        
        uid = uid if uid else self.__url(object)
        idxs = idxs if idxs !=[] else self.delegatedIndexes
        data = {'id' : uid}
        for name in idxs :
            attr = getattr(w, name, '')
            data[name] = attr() if callable(attr) else attr
        c = SolrConnection(self.solr_url)
        c.add(**data)
        txn = transaction.get()
        txn.addAfterCommitHook(SolrTransactionHook(c))
    
    
    # PortalCatalog api overloads
    security.declareProtected(ModifyPortalContent, 'indexObject')
    def indexObject(self, object) :
        """ Add to catalog and send to Solr """
        super(CatalogTool, self).indexObject(object)
        self.solrAdd(object)

    security.declarePrivate('reindexObject')
    def reindexObject(self, object, idxs=[], update_metadata=1, uid=None):
        super(CatalogTool, self).reindexObject(object,
                                               idxs=idxs,
                                               update_metadata=update_metadata,
                                               uid=uid)
        if idxs != []:
            # Filter out invalid indexes.
            valid_indexes = self._catalog.indexes.keys()
            idxs = [i for i in idxs if i in valid_indexes and i in self.delegatedIndexes]
        else :
            idxs = self.delegatedIndexes

        if idxs :
            self.solrAdd(object, idxs=idxs, uid=uid)
    
    security.declarePrivate('unindexObject')
    def unindexObject(self, object):
        """Remove from catalog.
        """
        super(CatalogTool, self).unindexObject(object)
        c = SolrConnection(self.solr_url)
        url = self.__url(object)
        c.delete(id=url)
        txn = transaction.get()
        txn.addAfterCommitHook(SolrTransactionHook(c))
        
InitializeClass(CatalogTool)


class DelegatedCatalog(Catalog) :
    '''C'est ici qu'on délègue effectivement à Solr '''
    def search(self, query, sort_index=None, reverse=0, limit=None, merge=1):
        return Catalog.search(self, query,
                              sort_index=sort_index,
                              reverse=reverse, limit=limit, merge=merge)