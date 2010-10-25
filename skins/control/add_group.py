##parameters=groupname, ajax=''
from Products.Plinn.utils import desacc
groupname = desacc(groupname).replace(' ', '-')
gp = context.acl_users.getGroupPrefix()
while groupname.startswith(gp) :
	groupname = groupname[len(gp):]

gtool = context.portal_groups
gtool.addGroup(groupname, **context.REQUEST.form)

from ZTUtils import make_query as mq
url = context.portal_url()
return context.REQUEST.RESPONSE.redirect('%s/portal_all_groups?%s' % (url, mq(portal_status_message = 'Group created.', ajax=ajax)))