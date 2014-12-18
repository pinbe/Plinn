""" Plinn permissions



"""
from AccessControl import Permissions
from AccessControl import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

security = ModuleSecurityInfo('Products.Plinn.permissions')

DeleteObjects = Permissions.delete_objects
security.declarePublic('DeleteObjects')

ViewHistory = Permissions.view_history
security.declarePublic('ViewHistory')

#
# Plinn Base Permissions
#


RemoveMember = 'Remove member'
security.declarePublic('RemoveMember')
setDefaultRoles( RemoveMember, ( 'Manager', ) )

SetLocalRoles = 'Set Local Roles'
security.declarePublic('SetLocalRoles')
setDefaultRoles( SetLocalRoles, ( 'Manager', 'Owner' ) )

DeleteOwnedObjects = 'Delete Owned Objects'
security.declarePublic('DeleteOwnedObjects')
setDefaultRoles( DeleteOwnedObjects, ('Owner', ) )

DeletePortalContents = 'Delete Portal Contents'
security.declarePublic('DeletePortalContents')
setDefaultRoles( DeletePortalContents, ('Manager', 'Owner') ) # + Member

SetMemberProperties = 'Set Member Properties'
security.declarePublic('SetMemberProperties')
setDefaultRoles( SetMemberProperties, ( 'Manager', ) )

SetMemberPassword = 'Set Member Password'
security.declarePublic('SetMemberPassword')
setDefaultRoles( SetMemberPassword, ( 'Manager', ) )

CheckMemberPermission = 'Check Member Permission'
security.declarePublic('CheckMemberPermission')
setDefaultRoles( CheckMemberPermission, ( 'Manager', ) )

ListNotificationSettings = 'List Notification Settings'
security.declarePublic('ListNotificationSettings')
setDefaultRoles( ListNotificationSettings, ( 'Manager', ) )

SubscribeNotification = 'Subscribe Notification'
security.declarePublic('SubscribeNotification')
setDefaultRoles( SubscribeNotification, ( 'Manager', 'Owmer') ) # + Reader

#
# Make public GRUF permissions
#
from Products.GroupUserFolder.GroupsToolPermissions import AddGroups, \
														   ManageGroups, \
														   ViewGroups, \
														   DeleteGroups, \
														   SetGroupOwnership

security.declarePublic('AddGroups')
security.declarePublic('ManageGroups')
security.declarePublic('ViewGroups')
security.declarePublic('DeleteGroups')
security.declarePublic('SetGroupOwnership')
