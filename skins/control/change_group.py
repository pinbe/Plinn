##parameters=groupId, title='', description='', createSharedFolder=None, ajax='', REQUEST=None

groupsTool = context.portal_groups
wGroup = groupsTool.getGroupById(groupId)
wGroup.setGroupProperties({'title' : title, 'description' : description})
if createSharedFolder :
	groupsTool.createGrouparea(groupId)

if REQUEST is not None :
	from ZTUtils import make_query as mq
	url = context.portal_url()
	red = context.REQUEST. RESPONSE.redirect
	return red('%s/group_data?%s' % (url, mq(group=groupId, ajax=ajax, portal_status_message='Group modified.')))