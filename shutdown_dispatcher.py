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
""" provides utilities to raise / handle zope server shutdown events

$Id: shutdown_dispatcher.py 1480 2009-03-19 19:15:52Z pin $
$URL: http://svn.cri.ensmp.fr/svn/Plinn/branches/CMF-2.1/shutdown_dispatcher.py $
"""

import asyncore
from zope.event import notify
from zope.component import getSiteManager
from events import ZopeShutdownEvent
from OFS.interfaces import IApplication

class ZopeShutdownDispatcher(asyncore.dispatcher):

	
	def __init__(self, app, map=None):
		asyncore.dispatcher.__init__(self, None, map)
		self.connected = False
		self.app = self._fileno = app
		self.add_channel()
	
	def close(self) :
		self.del_channel()

	def readable(self):
		return False

	def handle_read(self):
		return True

	def writable(self):
		return False

	def handle_write (self):
		return True
		
	def clean_shutdown_control(self, phase, time):
		asyncore.dispatcher.log_info(self, 'zope shutdown event raised at phase: %s' % phase, 'info')
		e = ZopeShutdownEvent(self.app, phase, time)
		notify(e)
		return e.veto
