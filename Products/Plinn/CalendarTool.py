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
""" Plinn calendar tool provides utilities to display content on a calendar layout



"""

from Products.CMFCore.utils import UniqueObject, getToolByName
from Products.CMFCore.permissions import ManagePortal, ListFolderContents
from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.ActionInformation import ActionInformation
from Products.CMFCore.ActionInformation import ActionInformation
from OFS.SimpleItem import SimpleItem
from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

import calendar
from DateTime import DateTime
from sets import Set
from types import StringType

class CalendarTool (UniqueObject, ActionProviderBase, SimpleItem):
	""" a calendar tool """
	id = 'portal_calendar'
	meta_type = 'Plinn Calendar Tool'
	security = ClassSecurityInfo()
	
	manage_options = ({ 'label' : 'Configure', 'action' : 'manage_configure' }, ) + \
						ActionProviderBase.manage_options + \
						SimpleItem.manage_options



	#
	#	ZMI methods
	#

	security.declareProtected( ManagePortal, 'manage_configure' )
	manage_configure = PageTemplateFile('www/configureCalendarTool', globals(),
								   __name__='manage_configure')

	def __init__(self) :
		calendar.setfirstweekday(0)
		self.dateIndexes = ['created', 'modified', 'DateTimeOriginal']
		self.displayRange = [0, 96]
		#calViewActionInfo = ActionInformation('calendar_view',
		#									  title = 'Calendar View',
		#									  category = 'folder',
		#									  permissions = (ListFolderContents, ),
		#									  condition = 'python: folder is object',
		#									  action = 'string: ${folder_url}/calendar_view')
		self._actions = tuple()
		
	security.declareProtected(ManagePortal, 'configureTool')
	def configureTool(self, dateIndexes, displayRange, REQUEST = None) :
		""" Define date indexes managed by this tool """
		self.dateIndexes = dateIndexes
		self.displayRange = map(lambda s : int(s) * 4, displayRange)
		if REQUEST :
			return self.manage_configure(self, REQUEST, manage_tabs_message='Saved changes.')
		
	security.declarePublic('getDateIndexes')
	def getDateIndexes(self) :
		""" Return managed date indexes """
		
		return self.dateIndexes
	
	security.declareProtected(ManagePortal, 'getCandidateIndexes')
	def getCandidateIndexes(self) :
		""" return portal_catalog date and field indexes """
		
		cTool = getToolByName(self, 'portal_catalog')
		fIndexes = [index.id for index in cTool.getIndexObjects() if index.meta_type == 'FieldIndex' or \
																	 index.meta_type == 'DateIndex' ]
		fIndexes.sort(lambda a, b : cmp(a.lower(), b.lower()))
		return fIndexes
	
	security.declarePublic('getCommonIndexes')
	def getCommonIndexes(self, objects) :
		""" Return indexes which belongs to all objects """
		
		if not objects :
			return Set([])
		types = []
		allIndexSets = []
		for ob in objects :
			if ob.meta_type in types :
				continue
			else :
				types.append(ob.meta_type)
				obIndexes = []
				for index in self.dateIndexes :
					if hasattr(ob, index) :
						obIndexes.append(index)
				allIndexSets.append(Set(obIndexes))
		return reduce(lambda a, b : a & b, allIndexSets, Set(self.dateIndexes))
		
	security.declarePublic('getDisplayRange')
	def getDisplayRange(self) :
		""" Return range to display in week view
		"""
		return self.displayRange
	
	security.declarePublic('indexIsCallable')
	def indexIsCallable(self, index, objects = []) :
		""" Return 1 if callable 0 if not callable or -1 if it's unknown """
		isCallable = -1
		if objects :
			if callable(getattr(objects[0], index)) :
				isCallable = 1
			else :
				isCallable = 0
		return isCallable

	security.declarePublic('buildDate')
	def buildDate(self, dateOrString) :
		""" Return DateTime instance """
		if type(dateOrString) == StringType :
			return DateTime(dateOrString)
		else :
			return dateOrString
	
	security.declarePrivate('listActions')
	def listActions(self, object=None) :
		""" List action according to indexes """
		
		actions = list(self._actions)

		if getattr(object, 'isAnObjectManager', False) :
			request = object.REQUEST
			
			visible = request['PATH_INFO'].split('/') [-1] == 'calendar_view' and True or False
			try :
				if hasattr(object, 'listNearestFolderContents') :
					objects = object.listNearestFolderContents()
				elif hasattr(object, 'listFolderContents') :
					objects = object.listFolderContents()
				else :
					objects = object.objectValues()
			except :
				objects = []
			
			if objects :
				for index in [ index for index in self.getCommonIndexes(objects) ] :
					ai = ActionInformation( index
										  , title = 'sort_by_index_%s' % index
										  , category = 'additional_tabs'
										  , action = 'string:${folder_url}/calendar_view?sortBy=' + index
										  , visible = visible)
					actions.append(ai)
			
		return actions
		
	security.declarePublic('sortObjectsByDate')
	def sortObjectsByDate(self, objects, index) :
		"""Sort objects by date index
		"""
		if objects :
			if callable(getattr(objects[0], index)) :
				objects.sort(lambda a, b : cmp(getattr(a, index)(), getattr(b, index)()))
			else :
				objects.sort(lambda a, b : cmp(getattr(a, index), getattr(b, index)))
		return objects
		
	security.declarePublic('getWeeksList')
	def getWeeksList(self, objects, index, year=2004, month=5) :
		"""Creates a series of weeks, each of which contains an integer day number.
		   A day number of 0 means that day is in the previous or next month.
		"""
		
		if objects :
			getIndexValue = callable(getattr(objects[0], index)) and \
								( lambda ob : getattr(ob, index)() ) or \
								( lambda ob : getattr(ob, index) )
			buildDate = type(getIndexValue(objects[0])) == StringType and \
							( lambda date : DateTime(date) ) or \
							( lambda date : date )
		weekList = []

		for week in calendar.monthcalendar(year, month) :
			weekInfoList = []
			
			for day in week :
				if day == 0 :
					inside = []
				else :
					inside = []
					outside = []
					for ob in objects :
						obDate = buildDate(getIndexValue(ob))
						if obDate.year() == year and obDate.month() == month and obDate.day() == day :
							inside.append(ob)
						else :
							outside.append(ob)
					objects = outside
				
				dayInfo = {'day' : day,
						   'objects' : inside}
				
				weekInfoList.append(dayInfo)
				
			weekList.append(weekInfoList)
	
		return weekList
	
	security.declarePublic('getDays')
	def getDays(self, letters=2):
		""" Returns a list of days with the correct start day first """
		return calendar.weekheader(letters).split()
	
	security.declarePublic('isToday')
	def isToday(self, year, month, day) :
		""" return True if date is Today False otherwise
		"""
		now = DateTime()
		if now.day() == day and now.month() ==	month and now.year() == year :
			return True
		else :
			return False
	
	security.declarePublic('getMonthName')
	def getMonthName(self, month) :
		""" return month name """
		return calendar.month_name[month]
	
	security.declarePublic('getNextMonth')
	def getNextMonth(self, year, month) :
		""" return next month """
		month += 1
		if month > 12 :
			month = 1
			year += 1
		return {'year' : year, 'month' : month}
	
	security.declarePublic('getPreviousMonth')
	def getPreviousMonth(self, year, month) :
		""" return previous month """
		month -= 1
		if month < 1 :
			month = 12
			year -= 1
		return {'year' : year, 'month' : month}
	
	security.declarePublic('getWeek')
	def getWeek(self, objects, index, year=2004, month=5, day=24) :
		""" return week info """
		
		weeksList = self.getWeeksList(objects, index, year=year, month=month)
		for weekIndex in range(len(weeksList)) :
			if day in [ entry['day'] for entry	in weeksList[weekIndex] ] :
				break
		week = weeksList[weekIndex]
				
		for entry in week :
			entry.update({'month' : month})
		
		previousWeeksList = None
		nextWeeksList = None
		
		if week[0]['day'] == 0 :
			nbOfDaysInMonthBefore = [ entry['day'] for entry in week ].count(0)
			previousMonth = self.getPreviousMonth(year, month)
			previousWeeksList = self.getWeeksList(objects, index, year=previousMonth['year'], month=previousMonth['month'])
			daysInPreviousMonth = previousWeeksList[-1][:nbOfDaysInMonthBefore]
			for entry in daysInPreviousMonth :
				entry.update({'month' : previousMonth['month']})
			
			daysInThisMonth = week[nbOfDaysInMonthBefore:]
			
			week = daysInPreviousMonth + daysInThisMonth
		elif week[-1]['day'] == 0 :
			nbOfDaysInMonthAfter = [ entry['day'] for entry in week ].count(0)
			nextMonth = self.getNextMonth(year, month)
			nextWeeksList = self.getWeeksList(objects, index, year=nextMonth['year'], month=nextMonth['month'])
			daysInNextMonth = nextWeeksList[0][-nbOfDaysInMonthAfter:]
			for entry in daysInNextMonth :
				entry.update({'month' : nextMonth['month']})
			
			daysInThisMonth = week[:7 - nbOfDaysInMonthAfter]
			
			week = daysInThisMonth + daysInNextMonth
			
		
		# previous week
		if weekIndex > 0 :
			previousStartDay = {'year'	: year,
								'month' : month,
								'day'	: weeksList[weekIndex - 1][-1]}
		elif previousWeeksList :
			previousStartDay = {'year'	: previousMonth['year'],
								'month' : previousMonth['month'],
								'day'	: previousWeeksList[-2][0]}
		else :
			# the first week of this month begin on monday
			previousMonth = self.getPreviousMonth(year, month)
			previousWeeksList = self.getWeeksList([], index, year=previousMonth['year'], month=previousMonth['month'])
			previousStartDay = {'year'	: previousMonth['year'],
								'month' : previousMonth['month'],
								'day'	: previousWeeksList[-1][0]}
			
			
		# next week
		if weekIndex < len(weeksList) - 1 :
			nextStartDay = {'year'	: year,
							'month' : month,
							'day'	: weeksList[weekIndex + 1][0]}
		elif nextWeeksList :
			nextStartDay = {'year'	: nextMonth['year'],
							'month' : nextMonth['month'],
							'day'	: nextWeeksList[1][0]}
		else :
			# the last week of this month ends on sunday
			nextMonth = self.getNextMonth(year, month)
			nextWeeksList = self.getWeeksList([], index, year=nextMonth['year'], month=nextMonth['month'])
			nextStartDay = {'year'	: nextMonth['year'],
							'month' : nextMonth['month'],
							'day'	: nextWeeksList[0][0]}
			
		
		return {'week' : week,
				'previousStartDay' : previousStartDay,
				'nextStartDay' : nextStartDay}
	
	security.declarePublic('getWeekTable')
	def getWeekTable(self, week, index, indexIsCallable) :
		""" Utility method for transposing getWeek result
			for an easy display in table.
		"""
		
		weekMatrix = [ [ [] for q in range(96)	] for d in range(7) ]

		getIndexValue = indexIsCallable and \
							( lambda ob : getattr(ob, index)() ) or \
							( lambda ob : getattr(ob, index) )
		reelRange = self.displayRange[:]
		for dayIndex in range(7) :
			dayInfo = week[dayIndex]
			for ob in dayInfo['objects'] :
				date = self.buildDate(getIndexValue(ob))
				
				minutesAfterMidnight = date.hour() * 60 + date.minute()
				cellIndex = minutesAfterMidnight / 15
				
				if cellIndex < reelRange[0] :
					reelRange[0] = cellIndex
				elif cellIndex >= reelRange[1] :
					reelRange[1] = cellIndex + 1
				
				weekMatrix[dayIndex][cellIndex].append(ob)
		
		reelRange[0] = reelRange[0] - reelRange[0] % 4
		reelRange[1] = reelRange[1] + reelRange[1] % 4
		
		return {'weekMatrix' : weekMatrix, 'range' : reelRange}

	
	security.declarePublic('getEventHeight')
	def getEventHeight(self, event) :
		""" Return event height
		"""
		ee = event.end()
		es = event.start()
		days = int( ee - es)
		if days == 0 :
			duration = ( ee.hour() * 60 + ee.minute() ) - ( es.hour() * 60 + es.minute() )
			height = duration / 15
			return height
		else :
			return 1
#			 raise ValueError, "%s event duration is more than 1 day" % event.id

InitializeClass(CalendarTool)