# -*- coding: utf-8 -*-
#######################################################################################
#   Plinn - http://plinn.org                                                          #
#   Copyright (C) 2005-2009  Benoît PIN <benoit.pin@ensmp.fr>                         #
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
Adapters to plug specific contentish interfaces to historycal interface.



"""

from Globals import InitializeClass
from AccessControl import ClassSecurityInfo
from Products.CMFCore.permissions import ModifyPortalContent
from permissions import ViewHistory
from difflib import SequenceMatcher
from ContentHistory import ContentHistory
from types import UnicodeType
from htmlentitydefs import name2codepoint
from cgi import escape
import re

rent = re.compile(r"&(?P<entName>[A-Za-z]+);")

class DocumentHistory(ContentHistory) :

	security = ClassSecurityInfo()
	
	security.declareProtected(ViewHistory, 'compare')
	def compare(self, leftkey, rightkey):
		leftRev, leftDate = self.getHistoricalRevisionByKey(leftkey)
		rightRev, rightDate = self.getHistoricalRevisionByKey(rightkey)
		
		left = leftRev.EditableBody()
		right = rightRev.EditableBody()
		
		infos = {'diff'			: html_ready_diff(left, right)
				,'leftDate'		: leftDate
				,'rightDate'	: rightDate
				,'structure'	: False}
		return infos
	
	security.declareProtected(ModifyPortalContent, 'restore')
	def restore(self, key):
		rev = self.getHistoricalRevisionByKey(key)[0]
		self._content.edit(rev.Format(), rev.EditableBody())
		

InitializeClass(DocumentHistory)

class FolderishHistory(ContentHistory) :
	
	security = ClassSecurityInfo()
	
	security.declareProtected(ViewHistory, 'compare')
	def compare(self, leftkey, rightkey):
		leftRev, leftDate = self.getHistoricalRevisionByKey(leftkey)
		rightRev, rightDate = self.getHistoricalRevisionByKey(rightkey)
		
		leftIds = leftRev.objectIds()
		leftTitleAndIds = []
		for id in leftIds :
			title = leftRev[id].Title()
			if title != id :
				leftTitleAndIds.append('%s (%s)' % (id, title))
			else :
				leftTitleAndIds.append('%s' % id)
		left = '\n'.join(leftTitleAndIds)

		rightIds = rightRev.objectIds()
		rightTitleAndIds = []
		for id in rightIds :
			title = rightRev[id].Title()
			if title != id :
				rightTitleAndIds.append('%s (%s)' % (id, title))
			else :
				rightTitleAndIds.append('%s' % id)
		right = '\n'.join(rightTitleAndIds)

		infos = {'diff'			: html_ready_diff(left, right)
				,'leftDate'		: leftDate
				,'rightDate'	: rightDate
				,'structure'	: True}
		return infos
	
	
	security.declareProtected(ModifyPortalContent, 'restore')
	def restore(self, key):
		pass

InitializeClass(FolderishHistory)
	
	
	

InitializeClass(FolderishHistory)

def html_ready_diff(left, right, n=3) :
	if isinstance(left, UnicodeType) :
		left = left.encode('utf-8')
	if isinstance(right, UnicodeType) :
		right = right.encode('utf-8')
	left = rent.sub(convertEnt, left)
	right = rent.sub(convertEnt, right)
	sm = SequenceMatcher()
	leftLines = left.splitlines()
	rightLines = right.splitlines()
	sm.set_seqs(leftLines, rightLines)
	
	groups = []
	for i, group in enumerate(sm.get_grouped_opcodes(n)) :
		groups.append([])
		infos = groups[i]
		for tag, i1, i2, j1, j2 in group :
			info = {'tag'	: tag
			       ,'left'	: '\n'.join(leftLines[i1:i2])
				   ,'right'	: '\n'.join(rightLines[j1:j2])}
			infos.append(info)
	return groups

def convertEnt(m):
	"""convert html entity to utf-8 encoded character
	"""
	return unichr(name2codepoint.get(m.group('entName'), 32)).encode('utf-8')
