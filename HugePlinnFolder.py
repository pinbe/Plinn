# -*- coding: utf-8 -*-
#######################################################################################
#   Plinn - http://plinn.org                                                          #
#   Copyright (C) 2005-2007  Benoît PIN <benoit.pin@ensmp.fr>                         #
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
""" Plinn implementation of CMFBTree



"""


from Products.BTreeFolder2.BTreeFolder2 import BTreeFolder2Base
from Products.ZCatalog.Lazy import LazyMap
from BTrees.IOBTree import IOBTree
from BTrees.OIBTree import OIBTree
from Folder import PlinnFolder
from zope.event import notify
try :
    from zope.app.container.contained import notifyContainerModified
except ImportError :
    ## Zope-2.13 compat
    from zope.container.contained import notifyContainerModified
from events import ObjectPositionModified
from zope.component.factory import Factory
from Products.CMFCore.permissions import AddPortalFolders, \
                                         ManageProperties, \
                                         AccessContentsInformation
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from types import StringType


class HugePlinnFolder(BTreeFolder2Base, PlinnFolder) :
    """ Plinn Folder for large set of objects
    """
    
    security = ClassSecurityInfo()
    
    __getitem__ = PlinnFolder.__getitem__
    
    def __init__(self, id, title='') :
        PlinnFolder.__init__(self, id, title)
        BTreeFolder2Base.__init__(self, id)

    def _initBTrees(self):
        super(HugePlinnFolder, self)._initBTrees()
        self._pos2id_index = IOBTree()
        self._id2pos_index = OIBTree()
    
    def _checkId(self, id, allow_dup=0) :
        PlinnFolder._checkId(self, id, allow_dup)
        BTreeFolder2Base._checkId(self, id, allow_dup)
    
    security.declareProtected(AddPortalFolders, 'manage_addHugePlinnFolder')
    def manage_addHugePlinnFolder(self, id, title='', REQUEST=None) :
        """ Add new a new HugePlinnFolder object with id *id*.
        """
        ob = HugePlinnFolder(id, title)
        self._setObject(id, ob)
        if REQUEST is not None :
            return self.folder_contents(self, REQUEST, portal_status_message='Folder added')
    
    def _setOb(self, id, object):
        super(HugePlinnFolder, self)._setOb(id, object)
        pos = self.objectCount() - 1
        self._pos2id_index[pos] = id
        self._id2pos_index[id] = pos
    
    def _delOb(self, id):
        pos = self._id2pos_index[id]
        self._id2pos_index.pop(id)
            
        for p in xrange(pos+1, self.objectCount()) :
            ident = self._pos2id_index[p]
            self._pos2id_index[p-1] = ident
            self._id2pos_index[ident] = p-1
        
        self._pos2id_index.pop(self.objectCount()-1)

        super(HugePlinnFolder, self)._delOb(id)
            
    security.declareProtected(AccessContentsInformation, 'objectIds')
    def objectIds(self, spec=None) :
        if spec is not None :
            return super(HugePlinnFolder, self).objectIds(spec)
        
        pos2id = lambda pos : self._pos2id_index[pos]
        return LazyMap(pos2id, xrange(self.objectCount()))
        


    security.declareProtected(ManageProperties, 'moveObjectsByDelta')
    def moveObjectsByDelta(self, ids, delta, subset_ids=None,
                           suppress_events=False):
        """ Move specified sub-objects by delta.
        """
        if isinstance(ids, StringType):
            ids = (ids,)

        id2pos = self._id2pos_index
        pos2id = self._pos2id_index
        for id in ids :
            oldPosition = id2pos[id]
            newPosition = max(oldPosition + delta, 0)
            
            shift = delta > 0 and 1 or -1
            for p in xrange(oldPosition, newPosition, shift) :
                ident = pos2id[p+shift]
                pos2id[p] = ident
                id2pos[ident] = p
                if not suppress_events :
                    notify(ObjectPositionModified(self[ident], self, p))
            
            id2pos[id] = newPosition
            pos2id[newPosition] = id
            if not suppress_events :
                notify(ObjectPositionModified(self[id], self, newPosition))
        
        if not suppress_events :
            notifyContainerModified(self)
    
    security.declareProtected(ManageProperties, 'moveObjectsAfter')
    def moveObjectsAfter(self, ids, targetId, suppress_events=False):
        assert targetId not in ids

        # id2pos = dict(self._id2pos_index).copy()
        # pos2id = dict(self._pos2id_index).copy()
        id2pos = self._id2pos_index
        pos2id = self._pos2id_index
        targetPos = id2pos[targetId]
        minMovedPos = min([id2pos[id] for id in ids])
        maxMovedPos = max([id2pos[id] for id in ids])
        
        for id in ids :
            assert id == pos2id.pop(id2pos.pop(id))
        
        id2posUpdate = {}
        pos2idUpdate = {}

        if targetPos < minMovedPos :
            # selection moved before the first item position
            for i, id in enumerate(ids) :
                pos = i + targetPos + 1
                id2posUpdate[id] = pos
                pos2idUpdate[pos] = id

            for id in IndexIterator(pos2id, maxMovedPos, start=targetPos+1):
                pos = pos + 1
                id2posUpdate[id] = pos
                pos2idUpdate[pos] = id
            
        elif targetPos > minMovedPos and targetPos < maxMovedPos :
            print minMovedPos, maxMovedPos, targetPos
            print "déposé entre la première et la dernière de la sélection"
            raise NotImplementedError()
        else :
            # selection moved after the last item position
            pos = minMovedPos
            for id in IndexIterator(pos2id, targetPos, start=minMovedPos+1) :
                id2posUpdate[id] = pos
                pos2idUpdate[pos] = id
                pos += 1
            
            pos = targetPos - len(ids) + 1
            for id in ids :
                id2posUpdate[id] = pos
                pos2idUpdate[pos] = id
                pos +=1
        
        id2pos.update(id2posUpdate)
        pos2id.update(pos2idUpdate)
        
        # just for debug
        for pos in xrange(len(self)) :
            assert pos2id.has_key(pos)
            assert id2pos.has_key(pos2id[pos])
        
        if not suppress_events :
            for id, pos in id2posUpdate.items() :
                notify(ObjectPositionModified(self[id], self, pos))
                
            notifyContainerModified(self)
    
    def getObjectPosition(self, id):
        """ Get the position of an object by its id.
        """
        try :
            return self._id2pos_index[id]
        except KeyError :
            raise ValueError('The object with the id "%s" does not exist.' % id)


class IndexIterator :
    def __init__(self, d, maxPos, start=0, length=None) :
        self.d = d
        self.pos = start
        self.maxPos = maxPos
        self.length = length
        self.fetchedValuesCpt = 0
    
    def __iter__(self) :
        return self
    
    def next(self) :
        try :
            if self.pos > self.maxPos or \
                 self.fetchedValuesCpt == self.length:
                raise StopIteration
            v = self.d[self.pos]
            self.pos = self.pos + 1
            self.fetchedValuesCpt = self.fetchedValuesCpt + 1
            return v
        except KeyError :
            self.pos = self.pos + 1
            return self.next()
    

InitializeClass(HugePlinnFolder)
HugePlinnFolderFactory = Factory(HugePlinnFolder)
manage_addHugePlinnFolder = HugePlinnFolder.manage_addHugePlinnFolder.im_func
