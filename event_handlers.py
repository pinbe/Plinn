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
Plinn event handlers.

$Id: event_handlers.py 1517 2009-06-30 12:54:52Z pin $
$URL: http://svn.cri.ensmp.fr/svn/Plinn/branches/CMF-2.1/event_handlers.py $
"""
from zope.app.container.interfaces import IObjectRemovedEvent
from Products.CMFCore.utils import getToolByName
from Products.Plinn.utils import getAdapterByInterface
from quopri import encodestring

def reindexObjectPosition(event) :
	event.object.reindexObject(idxs=['position'])

def handleObjectRemoved(ob, event) :
	folder = event.oldParent
	settings = getAdapterByInterface(folder, 'Products.Plinn.interfaces.IEmailNotificationSettings', None)
	if settings :
		subscribers = settings.getSubscribersFor('zope.app.container.interfaces.IObjectRemovedEvent')
		addresses = map(encodeAdr, subscribers)
		addresses = filter(None, addresses)
		if not addresses :
			return
		addresses = ', '.join(addresses)
		recipientsHeader = 'Bcc: %s' % addresses
		portal = getToolByName(folder, 'portal_url').getPortalObject()
		email_from_address = portal.email_from_address
		subject = "Suppression d'un élément"
		text_body = "Le document « %s » vient d'être supprimé du portail %s.\n\nIl était placé à l'url :\n%s" % \
					(ob.title_or_id(), portal.Title(), ob.absolute_url())
		message = folder.echange_mail_template(  From = email_from_address
												, recipients = recipientsHeader
												, Subject = "=?utf-8?q?%s?=" % encodestring(subject).replace('=\n', '')
												, ContentType = 'text/plain'
												, charset = 'UTF-8'
												, body=text_body)
		MailHost = portal.MailHost
		MailHost.send( message.encode('utf-8') )
		
		
def encodeAdr(member) :
	name = member.getMemberFullName(nameBefore=0)
	email = member.getProperty('email')
	qpName = encodestring(name).replace('=\n', '')
	return '''"=?utf-8?q?%s?=" <%s>''' % (qpName, email)
