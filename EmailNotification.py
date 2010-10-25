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
Module to manage email notification settings.

$Id: EmailNotification.py 1516 2009-06-29 14:12:14Z pin $
$URL: http://svn.cri.ensmp.fr/svn/Plinn/branches/CMF-2.1/EmailNotification.py $
"""
from ExtensionClass import Base
import Acquisition
from Globals import InitializeClass, PersistentMapping
from AccessControl import ClassSecurityInfo
from zope.interface import implements
from interfaces import IEmailNotificationSettings
from permissions import ListNotificationSettings, SubscribeNotification
from Products.CMFCore.utils import getToolByName
from Products.Plinn.utils import Message as _

NOTIFICATION_SETTINGS_NAME = '_notification_settings'
EVENTS = ({'interface':'zope.app.container.interfaces.IObjectRemovedEvent'
		  ,'title':_(u'Object deleted')},)

class EmailNoticationSettings(Base, Acquisition.Implicit):
	"""
	Adapter used to map users on objects and send them email notification about events.
	Provide methods to resolve recipients list for a notification.
	"""
	
	implements(IEmailNotificationSettings)
	security = ClassSecurityInfo()
	
	def __init__(self, content) :
		self._content = content
		if not hasattr(content.aq_base, NOTIFICATION_SETTINGS_NAME) :
			setattr(content, NOTIFICATION_SETTINGS_NAME, PersistentMapping())
	
	def _getSettings(self) :
		return getattr(self._content, NOTIFICATION_SETTINGS_NAME)
	
	security.declarePrivate('getSubscribersFor')
	def getSubscribersFor(self, eventIFace):
		"""returns subscribers for event interface"""
		settings = self._getSettings()
		mtool = getToolByName(self, 'portal_membership')
		memberIds = [mid for mid, mSettings in settings.items() if mSettings.get(eventIFace, False)]
		
		return mtool.getMembers(memberIds)
	
	security.declareProtected(SubscribeNotification, 'subscribeToEvent')
	def subscribeToEvent(self, eventIFace, register):
		settings = self._getSettings()
		mtool = getToolByName(self, 'portal_membership')
		m = mtool.getAuthenticatedMember()
		mid = m.getId()
		if not settings.has_key(mid) :
			settings[mid] = PersistentMapping()
		
		memberSettings = settings[mid]
		memberSettings[eventIFace] = register
		
	security.declareProtected(SubscribeNotification, 'myNotifications')
	def myNotifications(self):
		settings = self._getSettings()
		mtool = getToolByName(self, 'portal_membership')
		m = mtool.getAuthenticatedMember()
		mid = m.getId()
		mySettings = settings.get(mid, {})
		
		notifications = []
		for event in EVENTS :
			setting = event.copy()
			setting['registered'] = mySettings.get(event['interface'], False)
			notifications.append(setting)
		
		return notifications
	
	security.declarePublic('getManagedEvents')
	def getManagedEvents(self):
		return [e['interface'] for e in EVENTS]
		
		

InitializeClass(EmailNoticationSettings)