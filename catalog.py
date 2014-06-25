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

# imports for Catalog class
from Products.PluginIndexes.interfaces import ILimitedResultIndex
from Products.ZCatalog.Lazy import LazyMap, LazyCat, LazyValues
from BTrees.IIBTree import intersection, IISet
from BTrees.IIBTree import weightedIntersection
import warnings

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
    meta_type = 'Plinn Catalog'
    security = ClassSecurityInfo()
    manage_options = (BaseCatalogTool.manage_options[:5] +
                      ({'label' : 'Solr', 'action' : 'manage_solr'},) +
                      BaseCatalogTool.manage_options[5:])
    manage_solr = PageTemplateFile('www/manage_solr', globals())
    
    
    def __init__(self, idxs=[]) :
        super(CatalogTool, self).__init__()
        self._catalog = DelegatedCatalog(self)
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
    
    def __init__(self, zcat, brains=None) :
        Catalog.__init__(self, brains=brains)
        self.zcat = zcat
    
    def delegateSearch(self, query, plan) :
        '''
        retours faux : 
        None signifie : pas de délégation, il faut continuer à interroger les autres index.
        IISet() vide : pas de résultat lors de la délégation, on peut arrêter la recherche.
        '''
        indexes = set(query.keys()).intersection(set(self.zcat.delegatedIndexes))
        if not indexes :
            return None
        delegatedQuery = {}
        for i in indexes :
            delegatedQuery[i] = query.pop(i)
            try : plan.remove(i)
            except ValueError : pass
        c = SolrConnection(self.zcat.solr_url)
        q =' AND '.join(['%s:"%s"' % item for item in delegatedQuery.items()])
        resp = c.query(q, fields='id', rows=len(self))
        c.close()
        return IISet(filter(None, [self.uids.get(r['id']) for r in resp.results])) 
    
    def search(self, query, sort_index=None, reverse=0, limit=None, merge=1):
        """Iterate through the indexes, applying the query to each one. If
        merge is true then return a lazy result set (sorted if appropriate)
        otherwise return the raw (possibly scored) results for later merging.
        Limit is used in conjuntion with sorting or scored results to inform
        the catalog how many results you are really interested in. The catalog
        can then use optimizations to save time and memory. The number of
        results is not guaranteed to fall within the limit however, you should
        still slice or batch the results as usual."""

        rs = None # resultset

        # Indexes fulfill a fairly large contract here. We hand each
        # index the query mapping we are given (which may be composed
        # of some combination of web request, kw mappings or plain old dicts)
        # and the index decides what to do with it. If the index finds work
        # for itself in the query, it returns the results and a tuple of
        # the attributes that were used. If the index finds nothing for it
        # to do then it returns None.

        # Canonicalize the request into a sensible query before passing it on
        query = self.make_query(query)

        cr = self.getCatalogPlan(query)
        cr.start()

        plan = cr.plan()
        if not plan:
            plan = self._sorted_search_indexes(query)
        
        # délégation
        rs = self.delegateSearch(query, plan)
        if rs is not None and not rs :
            return LazyCat([])

        indexes = self.indexes.keys()
        for i in plan:
            if i not in indexes:
                # We can have bogus keys or the plan can contain index names
                # that have been removed in the meantime
                continue

            index = self.getIndex(i)
            _apply_index = getattr(index, "_apply_index", None)
            if _apply_index is None:
                continue

            cr.start_split(i)
            limit_result = ILimitedResultIndex.providedBy(index)
            if limit_result:
                r = _apply_index(query, rs)
            else:
                r = _apply_index(query)

            if r is not None:
                r, u = r
                # Short circuit if empty result
                # BBB: We can remove the "r is not None" check in Zope 2.14
                # once we don't need to support the "return everything" case
                # anymore
                if r is not None and not r:
                    cr.stop_split(i, result=None, limit=limit_result)
                    return LazyCat([])

                # provide detailed info about the pure intersection time
                intersect_id = i + '#intersection'
                cr.start_split(intersect_id)
                # weightedIntersection preserves the values from any mappings
                # we get, as some indexes don't return simple sets
                if hasattr(rs, 'items') or hasattr(r, 'items'):
                    _, rs = weightedIntersection(rs, r)
                else:
                    rs = intersection(rs, r)

                cr.stop_split(intersect_id)

                # consider the time it takes to intersect the index result with
                # the total resultset to be part of the index time
                cr.stop_split(i, result=r, limit=limit_result)
                if not rs:
                    break
            else:
                cr.stop_split(i, result=None, limit=limit_result)

        # Try to deduce the sort limit from batching arguments
        b_start = int(query.get('b_start', 0))
        b_size = query.get('b_size', None)
        if b_size is not None:
            b_size = int(b_size)

        if b_size is not None:
            limit = b_start + b_size
        elif limit and b_size is None:
            b_size = limit

        if rs is None:
            # None of the indexes found anything to do with the query
            # We take this to mean that the query was empty (an empty filter)
            # and so we return everything in the catalog
            warnings.warn('Your query %s produced no query restriction. '
                          'Currently the entire catalog content is returned. '
                          'In Zope 2.14 this will result in an empty LazyCat '
                          'to be returned.' % repr(cr.make_key(query)),
                          DeprecationWarning, stacklevel=3)

            rlen = len(self)
            if sort_index is None:
                sequence, slen = self._limit_sequence(self.data.items(), rlen,
                    b_start, b_size)
                result = LazyMap(self.instantiate, sequence, slen,
                    actual_result_count=rlen)
            else:
                cr.start_split('sort_on')
                result = self.sortResults(
                    self.data, sort_index, reverse, limit, merge,
                        actual_result_count=rlen, b_start=b_start,
                        b_size=b_size)
                cr.stop_split('sort_on', None)
        elif rs:
            # We got some results from the indexes.
            # Sort and convert to sequences.
            # XXX: The check for 'values' is really stupid since we call
            # items() and *not* values()
            rlen = len(rs)
            if sort_index is None and hasattr(rs, 'items'):
                # having a 'items' means we have a data structure with
                # scores.  Build a new result set, sort it by score, reverse
                # it, compute the normalized score, and Lazify it.

                if not merge:
                    # Don't bother to sort here, return a list of
                    # three tuples to be passed later to mergeResults
                    # note that data_record_normalized_score_ cannot be
                    # calculated and will always be 1 in this case
                    getitem = self.__getitem__
                    result = [(score, (1, score, rid), getitem)
                            for rid, score in rs.items()]
                else:
                    cr.start_split('sort_on')

                    rs = rs.byValue(0) # sort it by score
                    max = float(rs[0][0])

                    # Here we define our getter function inline so that
                    # we can conveniently store the max value as a default arg
                    # and make the normalized score computation lazy
                    def getScoredResult(item, max=max, self=self):
                        """
                        Returns instances of self._v_brains, or whatever is
                        passed into self.useBrains.
                        """
                        score, key = item
                        r=self._v_result_class(self.data[key])\
                              .__of__(aq_parent(self))
                        r.data_record_id_ = key
                        r.data_record_score_ = score
                        r.data_record_normalized_score_ = int(100. * score / max)
                        return r

                    sequence, slen = self._limit_sequence(rs, rlen, b_start,
                        b_size)
                    result = LazyMap(getScoredResult, sequence, slen,
                        actual_result_count=rlen)
                    cr.stop_split('sort_on', None)

            elif sort_index is None and not hasattr(rs, 'values'):
                # no scores
                if hasattr(rs, 'keys'):
                    rs = rs.keys()
                sequence, slen = self._limit_sequence(rs, rlen, b_start,
                    b_size)
                result = LazyMap(self.__getitem__, sequence, slen,
                    actual_result_count=rlen)
            else:
                # sort.  If there are scores, then this block is not
                # reached, therefore 'sort-on' does not happen in the
                # context of a text index query.  This should probably
                # sort by relevance first, then the 'sort-on' attribute.
                cr.start_split('sort_on')
                result = self.sortResults(rs, sort_index, reverse, limit,
                    merge, actual_result_count=rlen, b_start=b_start,
                    b_size=b_size)
                cr.stop_split('sort_on', None)
        else:
            # Empty result set
            result = LazyCat([])
        cr.stop()
        return result
