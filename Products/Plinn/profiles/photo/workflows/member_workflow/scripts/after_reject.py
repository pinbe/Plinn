## Script (Python) "after_reject"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=sci
##title=
##
from Products.CMFCore.utils import getToolByName
mtool = getToolByName(context, 'portal_membership')
portal = context.portal_url.getPortalObject()
MailHost = portal.MailHost
from quopri import encodestring

def encodeAdr(member) :
	name = member.getMemberFullName(nameBefore=0)
	email = member.getProperty('email')
	qpName = encodestring(name).replace('=\n', '')
	return '''"=?utf-8?q?%s?=" <%s>''' % (qpName, email)


member = sci.object

sender = mtool.getAuthenticatedMember()
sender = encodeAdr(sender)
mto = encodeAdr(member)

subject = sci.kwargs.get('subject', '').strip()
body = sci.kwargs.get('body', '').strip()

if not (subject and body) :
	raise ValueError, "You must send a consitent email to reject the membership request."

mtool.removeMembers(memberIds = [member.getId()])

message = context.echange_mail_template(  From = sender
										, To = mto
										, Subject = "=?utf-8?q?%s?=" % encodestring(subject).replace('=\n', '')
										, ContentType = 'text/plain'
										, charset = 'UTF-8'
										, body= body
										)

MailHost.send( message )
