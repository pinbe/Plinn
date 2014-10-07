# -*- coding: utf-8 -*-
from zope.publisher.browser import BrowserLanguages
from Products.CMFCore.utils import getUtilityByInterfaceName

class AuthenticatedUserLanguages(BrowserLanguages):

    def getPreferredLanguages(self) :
        mtool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IMembershipTool')
        if mtool.isAnonymousUser() :
            return super(AuthenticatedUserLanguages, self).getPreferredLanguages()
        else :
            m = mtool.getAuthenticatedMember()
            userLangs = m.getProperty('preferred_languages', [])[:]
            return userLangs or super(AuthenticatedUserLanguages, self).getPreferredLanguages()
