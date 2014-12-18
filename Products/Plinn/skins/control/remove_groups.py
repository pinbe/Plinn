##parameters=groups=[], ajax=''
sd = context.session_data_manager.getSessionData()
groupPrefix = context.acl_users.getGroupPrefix()
prefixLenght = len(groupPrefix)

if sd is not None :
	if sd.has_key('requestedGroup') and sd['requestedGroup'] in groups :
		sd['requestedGroup'] = None

context.portal_groups.removeGroups([ groupId[prefixLenght:] for groupId in groups], keep_workspaces=1)
from ZTUtils import make_query as mq
url = context.portal_url()
red = context.REQUEST.RESPONSE.redirect
msg = not groups and 'Please select one or more groups before.' or (len(groups) == 1 and 'Group deleted.' or 'Groups deleted.')
return red('%s/portal_all_groups?%s' % (url, mq(portal_status_message=msg, ajax=ajax)))
