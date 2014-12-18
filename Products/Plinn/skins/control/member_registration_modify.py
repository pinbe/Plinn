## Script (Python) "member_registration_modify"
##parameters=members=[], register=None, reject=None, ajax=''
##title=Modify the status of a content object

from Products.CMFCore.utils import getToolByName
from ZTUtils import make_query as mq
req = context.REQUEST
resp = req.RESPONSE

utool = getToolByName(context, 'portal_url')
portal = utool.getPortalObject()
mtool = getToolByName(portal, 'portal_membership')

workflow_action = ''
wfkw = {}

if register :
	members = [ mtool.getMemberById(entry['id']) for entry in members if entry.has_key('checked') ]
	workflow_action = 'register'
	nbMembers = len(members)
	if not nbMembers :
		message = 'Please select at least one member.'
	elif nbMembers == 1 :
		message = 'Member registered.'
	else :
		message = 'Members registered.'

elif reject :
	# handle form from reject_member_form
	members = [ mtool.getMemberById(entry['id']) for entry in members if entry.has_key('checked') ]
	workflow_action = 'reject'
	form = req.form
	wfkw['subject'] = form.get('subject', '')
	wfkw['body'] = form.get('body', '')
	message = 'Registration rejected.'

else :
	for m in members :
		if m.has_key('reject') :
			resp.redirect('%s/reject_member_form?%s' % ( portal.absolute_url(),
																	 mq(id=m['id'], ajax=ajax) ))
			return
	raise ValueError, 'No action selected.'

wtool = getToolByName(portal, 'portal_workflow')

for m in members:
	wtool.doActionFor(m, workflow_action, wf_id = 'member_workflow', **wfkw)



if ajax :
	query = mq(portal_status_message=message, ajax='1', syncFragments=['rightCell'] )
else :
	query = mq(portal_status_message=message)
redirect_url =	portal.absolute_url() + '/pending_members?'+ query

resp.redirect( redirect_url )