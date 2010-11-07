# -*- coding: utf-8 -*-
#######################################################################################
#   Plinn - http://plinn.org                                                          #
#   Copyright © 2009  Benoît PIN <benoit.pin@ensmp.fr>                                #
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
Plinn event interfaces.



"""
from zope.interface import Interface, Attribute

class IObjectPositionModified(Interface) :
	"""
	the object position has changed in his container
	"""
	
	object = Attribute("The object that change position.")
	parent = Attribute("The container of the object.")
	position = Attribute("The new position of the object in its container.")


class IZopeShutdownEvent(Interface) :
	"""
	zope is shuting down
	"""