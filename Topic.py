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
""" Plinn Topic



"""

from Globals import InitializeClass
from zope.component.factory import Factory
from AccessControl.SecurityInfo import ClassSecurityInfo
from Products.CMFCore.permissions import View, ListFolderContents
from Products.CMFTopic.permissions import AddTopics, ChangeTopics
from Products.CMFTopic.Topic import Topic as BaseTopic
from Products.CMFDefault.DublinCore import DefaultDublinCoreImpl
from Products.CMFCore.utils import getToolByName
from Folder import PlinnFolder
from types import ListType, TupleType, StringTypes

from sets import Set


class Topic(BaseTopic, PlinnFolder):
	""" CMF Topic with Dublin core metadata support """
	
	security = ClassSecurityInfo()
	
	security.declareProtected(ChangeTopics, 'listAvailableFields')
	def listAvailableFields( self ):
		""" Return a list of available fields for new criteria.
		"""
		fields = Set(BaseTopic.listAvailableFields(self))
		utool = getToolByName(self, "portal_url")
		portal = utool.getPortalObject()
		unusedTopicFields = Set(portal.getProperty("unused_topic_fields", []))
		return fields - unusedTopicFields
	
	security.declareProtected(View, 'queryCatalog')
	def queryCatalog(self, REQUEST=None, **kw) :
		""" Invoke the catalog using our criteria.
			remove Member Data results
		"""
		kw.update( self.buildQuery() )

		ttool = getToolByName(self, 'portal_types')
		if not kw.has_key('portal_type') :
			kw['portal_type'] = ttool.objectIds()
		else :
			if type(kw['portal_type']) == ListType :
				try : kw['portal_type'].remove('Member Data')
				except : pass
			if type(kw['portal_type']) == TupleType :
 				ptypes = list(kw['portal_type'])
				try :
					ptypes.remove('Member Data')
					kw['portal_type'] = tuple(ptypes)
				except : pass
			elif kw['portal_type'] == 'Member Data' :
				kw['portal_type'] = ttool.objectIds()

		portal_catalog = getToolByName( self, 'portal_catalog' )
		return portal_catalog.searchResults(REQUEST, **kw)
	
	
	security.declareProtected(ChangeTopics, 'loadSearchQuery')
	def loadSearchQuery(self, query):
		sort_on = query.pop('sort_on')
		sort_order = query.pop('sort_order')
		ctool = getToolByName(self, 'portal_catalog')
		hasindex = ctool._catalog.indexes.has_key
		
		for k, v in query.items() :
			if not hasindex(k) : continue
			if isinstance(v, StringTypes) :
				self.addCriterion(k, 'String Criterion')
				crit = self.getCriterion(k)
				crit.edit(v)
			elif isinstance(v, (ListType, TupleType)) :
				if len(v) == 1 :
					self.addCriterion(k, 'String Criterion')
					crit = self.getCriterion(k)
					crit.edit(v[0])
				else :	
					self.addCriterion(k, 'List Criterion')
					crit = self.getCriterion(k)
					crit.edit(value=v, operator='or')
			elif isinstance(v, dict) :
				self.addCriterion(k, v.pop('critType'))
				crit = self.getCriterion(k)
				crit.edit(**v)
		
		self.addCriterion(sort_on, 'Sort Criterion')
		sort_crit = self.getCriterion(sort_on)
		if sort_order == 'reverse' :
			sort_crit.edit(True)
		else :
			sort_crit.edit(False)
	
	security.declareProtected(ChangeTopics, 'getCompatibleCriteriaFor')
	def getCompatibleCriteriaFor(self, fieldName) :
		""" Return a list of criteria which belong to the field """
		
		pass	
InitializeClass(Topic)
TopicFactory = Factory(Topic)


def addTopic(dispatcher, id, title='', REQUEST=None):
	""" Create an empty topic.
	"""
	topic = Topic( id )
	topic.id = id
	topic.title = title
	dest = dispatcher.Destination()
	dest._setObject( id, topic )

	if REQUEST is not None:
		REQUEST['RESPONSE'].redirect( 'manage_main' )
