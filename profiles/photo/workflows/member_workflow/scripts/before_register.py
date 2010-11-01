## Script (Python) "before_register"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=sci
##title=
##
portal = sci.getPortal()
member = sci.object


from Products.Plinn.RegistrationTool import DEFAULT_MEMBER_GROUP
from Products.CMFCore.utils import getToolByName

gtool = getToolByName(portal, 'portal_groups')
mtool = getToolByName(portal, 'portal_membership')


if gtool.getGroupById(DEFAULT_MEMBER_GROUP) is None :
	gtool.addGroup(DEFAULT_MEMBER_GROUP)
	aclu = portal.acl_users
	aclu.changeUser(aclu.getGroupPrefix() + DEFAULT_MEMBER_GROUP, roles=['Member', ])

g = gtool.getGroupById(DEFAULT_MEMBER_GROUP)
g.addMember(member.getId())
