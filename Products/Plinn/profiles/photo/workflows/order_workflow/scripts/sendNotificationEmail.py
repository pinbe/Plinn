## Script (Python) "sendNotificationEmail"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=sci
##title=
##
from Products.photoprint.utils import translate
_ = lambda msg : translate(msg, context)
portal = context.portal_url.getPortalObject()

mtool = portal.portal_membership

recipients = sci.kwargs.get('recipients', [])
if not recipients :
	return []


MailHost = portal.MailHost
from quopri import encodestring

def encodeAdr(member) :
	name = member.getMemberFullName(nameBefore=0)
	email = member.getProperty('email')
	qpName = encodestring(name).replace('=\n', '')
	return '''"=?utf-8?q?%s?=" <%s>''' % (qpName, email)


object = sci.object

sender = mtool.getAuthenticatedMember()
sender = encodeAdr(sender)

recipientsFormated = map(encodeAdr, mtool.getMembers( recipients ))
mto = ', '.join(recipientsFormated)
if mto[-2:] == ', ' :
	mto = mto[:-2]

subject = sci.kwargs.get('subject', '')

body = []
pr = body.append
pr(sci.kwargs.get('comment', ''))

pr('')

trNumber = sci.kwargs.get('tracking_number', '')
if trNumber :
	pr(_('Tracking number').encode('utf-8') + ' ' + trNumber)

trUrl = sci.kwargs.get('tracking_url', '')
if trUrl :
	pr(_('Tracking url').encode('utf-8') + ' ' + trUrl)

body = '\n'.join(body)



message = context.echange_mail_template(  From = sender
										, To = mto
										, Subject = "=?utf-8?q?%s?=" % encodestring(subject).replace('=\n', '')
										, ContentType = 'text/plain'
										, charset = 'UTF-8'
										, body=body
										)


MailHost.send( message.encode('utf-8') )

return recipients
