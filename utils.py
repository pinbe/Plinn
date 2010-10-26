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
""" Plinn public utilities
$Id: utils.py 1534 2009-09-07 11:05:57Z pin $
$URL: http://svn.cri.ensmp.fr/svn/Plinn/branches/CMF-2.1/utils.py $
"""

import string
import re
from types import StringType
from random import randrange
from Acquisition import aq_base
from AccessControl.PermissionRole import rolesForPermissionOn
from AccessControl import ModuleSecurityInfo
from AccessControl import getSecurityManager
from AccessControl.User import UnrestrictedUser
from OFS.CopySupport import _cb_decode, _cb_encode, cookie_path
from Products.CMFCore.utils import getToolByName, getUtilityByInterfaceName
from Products.CMFCore.exceptions import BadRequest
from Products.Utf8Splitter.Utf8Splitter import Utf8Utils
from Globals import REPLACEABLE, NOT_REPLACEABLE, UNIQUE
from zope.i18n import translate as i18ntranslate
from zope.i18n.interfaces import IUserPreferredLanguages
from zope.i18nmessageid import MessageFactory
from zope.component.interfaces import ComponentLookupError
from zope.dottedname.resolve import resolve as resolve_dotted_name
from zope.component import queryAdapter

_marker = []

security = ModuleSecurityInfo( 'Products.Plinn.utils' )

security.declarePublic('thisObjectComeFromPortalSkin')
def thisObjectComeFromPortalSkin(ob, portal=None):
	""" check if ob comes from portal_skins """
	if not portal :
		portal = getToolByName(ob, 'portal_url')
		portal = portal.getPortalObject()
	
	if ob.aq_self == portal.aq_self :
		return False
	
	obId = ob.id
	if callable(obId) :
		obId = obId()
	
	sob = getattr(portal, obId, None)
		
	if sob is None :
		return False
	elif not(sob.aq_inner.aq_self is ob.aq_inner.aq_self) :
		return False
	else :
		try :
			portal._checkId(obId)
			return True
		except BadRequest :
			return False

security.declarePublic('listActionProviders_')
def listActionProviders_(context) :
	atool = getToolByName(context, 'portal_actions')
	return atool.listActionProviders()

def capitalizeCompoundGivenName(givenName) :
	givenName = givenName.strip()
	givenNames = ' '.join(givenName.split('-')).split()
	givenNameCapitalized = '-'.join(map(string.capitalize, givenNames))
	return givenNameCapitalized
				
			 
def formatFullName(memberName, memberGivenName, memberId, nameBefore=1) :
	memberFullName = ''
	if memberName and memberGivenName :
		if nameBefore :
			memberFullName = memberName.capitalize() + ' ' + capitalizeCompoundGivenName(memberGivenName)
		else :
			memberFullName = capitalizeCompoundGivenName(memberGivenName) + ' ' + memberName.capitalize() 
		
	elif memberName and not memberGivenName :
		memberFullName = memberName.capitalize()
		
	elif not memberName and memberGivenName :
		memberFullName = capitalizeCompoundGivenName(memberGivenName)
		
	else :
		memberFullName = memberId
	
	return memberFullName

# from OFS.ObjectManager #63
bad_url_chars = re.compile(r'[^a-zA-Z0-9-_~,.$\(\)@]')

security.declarePublic('makeValidId')
def makeValidId(self, id, allow_dup=0):
	id = Utf8Utils.desacc(id)
	id = bad_url_chars.sub('-', id)
	# If allow_dup is false, an error will be raised if an object
	# with the given id already exists. If allow_dup is true,
	# only check that the id string contains no illegal chars;
	# check_valid_id() will be called again later with allow_dup
	# set to false before the object is added.
	
	makeRandomId = False
	if id in ('.', '..'):
		makeRandomId = True
	if id.startswith('_'):
		id = id.lstrip('_')
	if id.startswith('aq_'): 
		id = id[3:]
	
	while id.endswith('__') :
		id = id[:-1]
	if not allow_dup:
		obj = getattr(self, id, None)
		if obj is not None:
			# An object by the given id exists either in this
			# ObjectManager or in the acquisition path.
			flags = getattr(obj, '__replaceable__', NOT_REPLACEABLE)
			if hasattr(aq_base(self), id):
				# The object is located in this ObjectManager.
				if not flags & REPLACEABLE:
					makeRandomId = True
				# else the object is replaceable even if the UNIQUE
				# flag is set.
			elif flags & UNIQUE:
				makeRandomId = True
	if id == 'REQUEST':
		makeRandomId = True
	
	if makeRandomId is True :
		id = str(randrange(2,10000)) + id
	return id
	
	

def _checkMemberPermission(userid, permission, obj, StringType = type('')):
	user = obj.aq_inner.acl_users.getUser(userid)
	roles = rolesForPermissionOn(permission, obj)
	if type(roles) is StringType:
		roles=[roles]
	if user.allowed( obj, roles ):
		return 1
	return 0
	
def getCPInfo(self) :
	try: cp = _cb_decode(self.REQUEST['__cp'])
	except: return None
	return cp


def popCP(self, indexes=None) :
	try: cp = _cb_decode(self.REQUEST['__cp'])
	except: return
	
	paths = list(cp[1])
	if indexes is not None :
		indexes = list(indexes)
		indexes.sort()
		indexes.reverse()
		for index in indexes :
			paths.pop(index)
	else :
		paths.pop()
	
	if not paths :
		self.REQUEST.RESPONSE.expireCookie('__cp', path=self.REQUEST['BASEPATH1'] or "/")
	else :
		paths = tuple(paths)
		cp = _cb_encode( (cp[0], paths) )
		resp = self.REQUEST['RESPONSE']
		resp.setCookie('__cp', cp, path='%s' % cookie_path(self.REQUEST))

security.declarePublic('Message')
Message = MessageFactory('plinn')

security.declarePublic('translate')
def translate(message, context):
	""" Translate i18n message.
	"""
	if isinstance(message, Exception):
		try:
			message = message[0]
		except (TypeError, IndexError):
			pass
	return i18ntranslate(message, domain='plinn', context=context.REQUEST)

security.declarePublic('desacc')
desacc = Utf8Utils.desacc

security.declarePublic('getPreferredLanguages')
def getPreferredLanguages(context):
	""" returns browser prefered languages"""
	request = getattr(context, 'REQUEST', None)
	if request is not None :
		adapter = IUserPreferredLanguages(request, None)
		if adapter is not None :
			return adapter.getPreferredLanguages()
	return []

security.declarePublic('getBestTranslationLanguage')
def getBestTranslationLanguage(langs, context):
	""" returns best translation language according
		availables languages (param langs)
		and user preferences (retrieves by context)
	"""
	request = getattr(context, 'REQUEST', None)
	if request :
		negociator = getUtilityByInterfaceName('zope.i18n.interfaces.INegotiator')
		return negociator.getLanguage(langs, request) or langs[0]
	else :
		return langs[0]

security.declarePublic('getAdapterByInterface')
def getAdapterByInterface(ob, dotted_name, default=_marker) :
	""" Get the adapter which provides the interface on the given object.
	"""
	try:
		iface = resolve_dotted_name(dotted_name)
	except ImportError:
		if default is _marker:
			raise ComponentLookupError, dotted_name
		return default

	adapter = queryAdapter(ob, iface, default=default)
	if adapter is _marker :
		raise ComponentLookupError, "no adapter providing %r found on %r" % (dotted_name, ob)

	# the adapter must be wrapped to allow security mahinery to work.
	if adapter != default :
		return adapter.__of__(ob)
	else :
		return default

def _sudo(func, userid=None) :
	"""
	execute func or any callable object
	without restriction. Used to switch off
	security assertions (eg. checkPermission) encountered
	during the execution.
	"""
	
	sm = getSecurityManager()
	restrictedUser = sm.getUser()
	
	if not userid :
		userid = restrictedUser.getId()
	
	sm._context.user = UnrestrictedUser(userid, '', (), ())

	deferedEx = None
	try :
		ret = func()
	except Exception, e :
		deferedEx = e
	
	sm._context.user = restrictedUser
	
	if deferedEx is not None :
		raise e

	return ret
	