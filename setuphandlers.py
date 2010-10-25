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
""" Plinn specific GenericSetup handlers

$Id: setuphandlers.py 1333 2008-07-31 12:10:34Z pin $
$URL: http://svn.cri.ensmp.fr/svn/Plinn/branches/CMF-2.1/setuphandlers.py $
"""

from Products.CMFCore.utils import getToolByName
from Products.PythonScripts.PythonScript import PythonScript

VARIOUS_FILENAME = 'various.py'


def importVarious(context) :
	""" exec python code from setup python script """
	site = context.getSite()
	text = context.readDataFile(VARIOUS_FILENAME)
	
	if not text : return
	
	site._setPortalTypeName('CMF Site')
	
	script = PythonScript('various')
	script = script.__of__(site)
	script.write(text)
	out = script(site)
	
	# clone current authenticated user into portal's acl_users
	from AccessControl import getSecurityManager
	sm = getSecurityManager()
	user = sm.getUser()
	mtool = getToolByName(site, 'portal_membership')
	mtool.addMember(user.getId(), user._getPassword(), user.getRoles(), user.getDomains())
	
	return out

def exportVarious(exportContext):
	site = exportContext.getSite()
	
	stool = getToolByName(site, 'portal_setup')
	importContext = stool._getImportContext(stool.getBaselineContextID())
	
	exportContext.writeDataFile( VARIOUS_FILENAME,
								 importContext.readDataFile(VARIOUS_FILENAME),
								 'text/plain' )
	
	return 'Various Plinn settings exported.'