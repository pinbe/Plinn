##parameters=
aclu = context.acl_users
groupPrefix = aclu.getGroupPrefix()
gtool = context.portal_groups
from ZTUtils import SimpleTreeMaker

def getGroups(object) :
	""" return children groups """
	if object is aclu :
		return gtool.getGroups(gtool.getRootGroups())
	else :
		return gtool.getGroups(gtool.getGroupsOfGroup(object.id))
	
stm = SimpleTreeMaker("group_tree")
stm.setChildAccess(function = getGroups)
stm.setIdAttr('id')

tree, rows = stm.cookieTree(aclu)
return {'tree' : tree, 'rows' : rows}