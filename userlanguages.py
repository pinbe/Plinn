# -*- coding: utf-8 -*-
from zope.publisher.browser import BrowserLanguages
from Products.CMFCore.utils import getUtilityByInterfaceName
from zope.component.interfaces import ComponentLookupError

class AuthenticatedUserLanguages(BrowserLanguages):

    def getPreferredLanguages(self) :
        try :
            mtool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IMembershipTool')
        except ComponentLookupError :
            return super(AuthenticatedUserLanguages, self).getPreferredLanguages()
        if mtool.isAnonymousUser() :
            return super(AuthenticatedUserLanguages, self).getPreferredLanguages()
        else :
            m = mtool.getAuthenticatedMember()
            userLangs = m.getProperty('preferred_languages', [])[:]
            return userLangs or super(AuthenticatedUserLanguages, self).getPreferredLanguages()
