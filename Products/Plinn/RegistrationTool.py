# -*- coding: utf-8 -*-
#######################################################################################
#   Plinn - http://plinn.org                                                          #
#   © 2005-2013  Benoît PIN <pin@cri.ensmp.fr>                                        #
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
""" Plinn registration tool: implements 3 modes to register members:
    anonymous, manager, reviewed.



"""

from Globals import InitializeClass, PersistentMapping
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFDefault.RegistrationTool import RegistrationTool as BaseRegistrationTool
from AccessControl import ClassSecurityInfo, ModuleSecurityInfo
from AccessControl.Permission import Permission
from BTrees.OOBTree import OOBTree
from Products.CMFCore.permissions import ManagePortal, AddPortalMember
from Products.CMFCore.exceptions import AccessControl_Unauthorized
from Products.CMFDefault.exceptions import EmailAddressInvalid
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.utils import getUtilityByInterfaceName
from Products.CMFCore.utils import _checkPermission
from Products.CMFDefault.utils import checkEmailAddress
from Products.GroupUserFolder.GroupsToolPermissions import ManageGroups
from Products.Plinn.utils import Message as _
from Products.Plinn.utils import translate
from Products.Plinn.utils import encodeQuopriEmail
from Products.Plinn.utils import encodeMailHeader
from DateTime import DateTime
from types import TupleType, ListType
from uuid import uuid4
import re

security = ModuleSecurityInfo('Products.Plinn.RegistrationTool')
MODE_ANONYMOUS = 'anonymous'
security.declarePublic('MODE_ANONYMOUS')

MODE_PASS_ANONYMOUS = 'pass_anonymous'
security.declarePublic('MODE_PASS_ANONYMOUS')

MODE_MANAGER = 'manager'
security.declarePublic('MODE_MANAGER')

MODE_REVIEWED = 'reviewed'
security.declarePublic('MODE_REVIEWED')

MODES = [MODE_ANONYMOUS, MODE_PASS_ANONYMOUS, MODE_MANAGER, MODE_REVIEWED]
security.declarePublic('MODES')

DEFAULT_MEMBER_GROUP = 'members'
security.declarePublic('DEFAULT_MEMBER_GROUP')



class RegistrationTool(BaseRegistrationTool) :

    """ Create and modify users by making calls to portal_membership.
    """

    meta_type = "Plinn Registration Tool"
    default_member_id_pattern = "^[A-Za-z][A-Za-z0-9_\.\-@]*$" # valid email allowed as member id
    _ALLOWED_MEMBER_ID_PATTERN = re.compile(default_member_id_pattern)

    manage_options = ({'label' : 'Registration mode', 'action' : 'manage_regmode'}, ) + \
                        BaseRegistrationTool.manage_options

    security = ClassSecurityInfo()

    security.declareProtected( ManagePortal, 'manage_regmode' )
    manage_regmode = PageTemplateFile('www/configureRegistrationTool', globals(),
                                        __name__='manage_regmode')

    def __init__(self) :
        self._mode = MODE_ANONYMOUS
        self._chain = ''
        self._passwordResetRequests = OOBTree()

    security.declareProtected(ManagePortal, 'configureTool')
    def configureTool(self, registration_mode, chain, REQUEST=None) :
        """ """

        if registration_mode not in MODES :
            raise ValueError, "Unknown mode: " + registration_mode
        else :
            self._mode = registration_mode
            self._updatePortalRoleMappingForMode(registration_mode)

        wtool = getToolByName(self, 'portal_workflow')

        if registration_mode == MODE_REVIEWED :
            if not hasattr(wtool, '_chains_by_type') :
                wtool._chains_by_type = PersistentMapping()
            wfids = []
            chain = chain.strip()

            if chain == '(Default)' :
                try : del wtool._chains_by_type['Member Data']
                except KeyError : pass
                self._chain = chain
            else :
                for wfid in chain.replace(',', ' ').split(' ') :
                    if wfid :
                        if not wtool.getWorkflowById(wfid) :
                            raise ValueError, '"%s" is not a workflow ID.' % wfid
                        wfids.append(wfid)

                wtool._chains_by_type['Member Data'] = tuple(wfids)
                self._chain = ', '.join(wfids)
        else :
            wtool._chains_by_type['Member Data'] = tuple()

        if REQUEST :
            REQUEST.RESPONSE.redirect(self.absolute_url() + '/manage_regmode?manage_tabs_message=Saved changes.')

    def _updatePortalRoleMappingForMode(self, mode) :

        urlTool = getToolByName(self, 'portal_url')
        portal = urlTool.getPortalObject()

        if mode in [MODE_ANONYMOUS, MODE_PASS_ANONYMOUS, MODE_REVIEWED] :
            portal.manage_permission(AddPortalMember, roles = ['Anonymous', 'Manager'], acquire=1)
        elif mode == MODE_MANAGER :
            portal.manage_permission(AddPortalMember, roles = ['Manager', 'UserManager'], acquire=0)

    security.declarePublic('getMode')
    def getMode(self) :
        # """ return current mode """
        return self._mode[:]

    security.declarePublic('getWfId')
    def getWfChain(self) :
        # """ return current workflow id """
        return self._chain

    security.declarePublic('roleMappingMismatch')
    def roleMappingMismatch(self) :
        # """ test if the role mapping is correct for the currrent mode """

        mode = self._mode
        urlTool = getToolByName(self, 'portal_url')
        portal = urlTool.getPortalObject()

        def rolesOfAddPortalMemberPerm() :
            p=Permission(AddPortalMember, [], portal)
            return p.getRoles()

        if mode in [MODE_ANONYMOUS, MODE_PASS_ANONYMOUS, MODE_REVIEWED] :
            if 'Anonymous' in rolesOfAddPortalMemberPerm() : return False

        elif mode == MODE_MANAGER :
            roles = rolesOfAddPortalMemberPerm()
            if 'Manager' in roles or 'UserManager' in roles and len(roles) == 1 and type(roles) == TupleType :
                return False

        return True

    security.declareProtected(AddPortalMember, 'addMember')
    def addMember(self, id, password, roles=(), groups=(DEFAULT_MEMBER_GROUP,), domains='', properties=None) :
        """ Idem CMFCore but without default role """

        if self.getMode() != MODE_REVIEWED :
            gtool = getToolByName(self, 'portal_groups')
            mtool = getToolByName(self, 'portal_membership')
            utool = getToolByName(self, 'portal_url')
            portal = utool.getPortalObject()

            if self.getMode() == MODE_PASS_ANONYMOUS :
                private_collections = portal.get('private_collections')
                if not private_collections :
                    raise AccessControl_Unauthorized()

                data = private_collections.data
                lines = filter(None, [l.strip() for l in data.split('\n')])
                assert len(lines) % 3 == 0
                collecInfos = {}
                for i in xrange(0, len(lines), 3) :
                    collecInfos[lines[i]] = {'pw' : lines[i+1],
                                             'path' : lines[i+2]}
                if not (collecInfos.has_key(properties.get('collection_id')) and \
                    collecInfos[properties.get('collection_id')]['pw'] == properties.get('collection_password')) :
                    raise AccessControl_Unauthorized('Wrong primary credentials')


            BaseRegistrationTool.addMember(self, id, password, roles=roles,
                                           domains=domains, properties=properties)

            isGrpManager = mtool.checkPermission(ManageGroups, portal) ## TODO : CMF2.1 compat
            aclu = self.aq_inner.acl_users

            for gid in groups:
                g = gtool.getGroupById(gid)
                if not isGrpManager :
                    if gid != DEFAULT_MEMBER_GROUP:
                        raise AccessControl_Unauthorized, 'You are not allowed to join arbitrary group.'

                if g is None :
                    gtool.addGroup(gid)
                aclu.changeUser(aclu.getGroupPrefix() +gid, roles=['Member', ])
                g = gtool.getGroupById(gid)
                g.addMember(id)
        else :
            BaseRegistrationTool.addMember(self, id, password, roles=roles,
                                           domains=domains, properties=properties)

    security.declarePublic( 'testPasswordValidity' )
    def testPasswordValidity(self, password, confirm=None):

        """ Verify that the password satisfies the portal's requirements.

        o If the password is valid, return None.
        o If not, return a string explaining why.
        """
        if not password:
            return _(u'You must enter a password.')

        if len(password) < 8 and not _checkPermission(ManagePortal, self):
            return _(u'Your password must contain at least 8 characters.')

        if confirm is not None and confirm != password:
            return _(u'Your password and confirmation did not match. '
                     u'Please try again.')

        return None



    def afterAdd(self, member, id, password, properties):
        """ notify member creation """
        member.notifyWorkflowCreated()
        member.indexObject()

    security.declarePublic('generatePassword')
    def generatePassword(self):
        """ This password may not been entered by user.
            Password generated by this method are typicaly used
            on a member registration with 'validate_email' option enabled.
        """
        return str(uuid4())

    security.declarePublic('requestPasswordReset')
    def requestPasswordReset(self, userid, initial=False, came_from=''):
        """ add uuid / (userid, expiration) pair
            if ok: send an email to member. returns error message otherwise.
        """
        self.clearExpiredPasswordResetRequests()
        mtool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IMembershipTool')
        member = mtool.getMemberById(userid)
        if not member :
            try :
                checkEmailAddress(userid)
                member = mtool.searchMembers('email', userid)
                if member :
                    userid = member[0]['username']
                    member = mtool.getMemberById(userid)
            except EmailAddressInvalid :
                pass
        if member :
            uuid = str(uuid4())
            while self._passwordResetRequests.has_key(uuid) :
                uuid = str(uuid4())
            self._passwordResetRequests[uuid] = (userid, DateTime() + 1, came_from)
            utool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IURLTool')
            ptool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IPropertiesTool')
            # fuck : mailhost récupéré avec getUtilityByInterfaceName n'est pas correctement
            # wrappé. Un « unrestrictedTraverse » ne marche pas.
            # mailhost = getUtilityByInterfaceName('Products.MailHost.interfaces.IMailHost')
            portal = utool.getPortalObject()
            mailhost = portal.MailHost
            sender = encodeQuopriEmail(ptool.getProperty('email_from_name'), ptool.getProperty('email_from_address'))
            to = encodeQuopriEmail(member.getMemberFullName(nameBefore=0), member.getProperty('email'))
            if initial :
                subject = translate(_('Complete your registration on the %s website')) % ptool.getProperty('title')
            else :
                subject = translate(_('How to reset your password on the %s website')) % ptool.getProperty('title')
            subject = encodeMailHeader(subject)
            options = {'initial' : initial,
                       'fullName' : member.getMemberFullName(nameBefore=0),
                       'member_id' : member.getId(),
                       'loginIsNotEmail' : member.getId() != member.getProperty('email'),
                       'siteName' : ptool.getProperty('title'),
                       'resetPasswordUrl' : '%s/password_reset_form/%s' % (utool(), uuid)}
            body = self.password_reset_mail(options)
            message = self.echange_mail_template(From=sender,
                                                 To=to,
                                                 Subject=subject,
                                                 ContentType = 'text/plain',
                                                 charset = 'UTF-8',
                                                 body=body)
            mailhost.send(message)
            return

        return _('Unknown user name. Please retry.')

    security.declarePrivate('clearExpiredPasswordResetRequests')
    def clearExpiredPasswordResetRequests(self):
        now = DateTime()
        for uuid, record in self._passwordResetRequests.items() :
            date = record[1]
            if date < now :
                del self._passwordResetRequests[uuid]


    security.declarePublic('resetPassword')
    def resetPassword(self, uuid, password, confirm) :
        record = self._passwordResetRequests.get(uuid)
        if not record :
            return None, _('Invalid reset password request.')

        userid, expiration, came_from = record
        now = DateTime()
        if expiration < now :
            self.clearExpiredPasswordResetRequests()
            return None, _('Your reset password request has expired. You can ask a new one.')

        msg = self.testPasswordValidity(password, confirm=confirm)
        if not msg : # None if everything ok. Err message otherwise.
            mtool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IMembershipTool')
            member = mtool.getMemberById(userid)
            if member :
                member.setSecurityProfile(password=password)
                del self._passwordResetRequests[uuid]
                return  {'userid': userid, 'came_from' : came_from}, _('Password successfully updated.')
            else :
                return None, _('"${userid}" username not found.', mapping={'userid': userid})
        else :
            return None, msg

InitializeClass(RegistrationTool)