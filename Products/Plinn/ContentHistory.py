# -*- coding: utf-8 -*-
#######################################################################################
#   Plinn - http://plinn.org                                                          #
#   Copyright © 2005-2009  Benoît PIN <benoit.pin@ensmp.fr>                           #
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
"""
Module to manage history of contents (comparisons, copy to present).



"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from ExtensionClass import Base
import Acquisition
from zope.interface import implements
from OFS.History import historicalRevision
from Products.PluginIndexes.common import safe_callable
from interfaces import IContentHistory
from Products.CMFCore.permissions import ModifyPortalContent
from permissions import ViewHistory
from struct import pack, unpack
from DateTime import DateTime

class ContentHistory(Base, Acquisition.Implicit) :
	""" Utility to manage historical entries of a content
	"""
	implements(IContentHistory)
	security = ClassSecurityInfo()
	
	def __init__(self, content) :
		self._content = content
	
	security.declareProtected(ViewHistory, 'listEntries')
	def listEntries(self, first=0, last=20):
		oid = self._content._p_oid
		db = self._content._p_jar.db()
		r = db.history(oid, size=last)

		if r is None:
			# storage doesn't support history
			return ()

		r=r[first:]

		for d in r:
			d['time']=DateTime(d['time'])
			d['key']='.'.join(map(str, unpack(">HHHH", d['tid'])))

		return r
	
	security.declareProtected(ViewHistory, 'getHistoricalRevisionByKey')
	def getHistoricalRevisionByKey(self, key, withContext=False):

		serial = apply(pack, ('>HHHH',) + tuple(map(int, key.split('.'))))
		content = self._content
		rev = historicalRevision(content, serial)
		rev = rev.__of__(content.aq_parent)
		if withContext is False :
			return rev, DateTime(rev._p_mtime)
		else :
			ctx = {}
			if isinstance(withContext, int) :
				first = max(withContext-1, 0)
				entries = self.listEntries(first=first, last=withContext+2)
			
			if len(entries) == 3 :
				ctx['next'], ctx['current'], ctx['previous'] = entries
			elif len(entries) == 2 :
				serials = [e['tid'] for e in entries]
				i =  serials.index(serial)
				if i == 0 :
					# last (newest) transaction
					ctx['current'], ctx['previous'] = entries
				else :
					ctx['next'], ctx['current'] = entries
			elif len(entries) == 1 :
				ctx['current'] = entries[0]
			return rev, ctx
				
	
	security.declareProtected(ViewHistory, 'compare')
	def compare(self, leftkey, rightkey):
		raise NotImplementedError
	
	
	security.declareProtected(ModifyPortalContent, 'restore')
	def restore(self, key):
		raise NotImplementedError
	
InitializeClass(ContentHistory)