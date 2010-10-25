## Script (Python) "sendNotificationEmail"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=sci
##title=
##
#TODO : translate messages
#from Products.PlacelessTranslationService.MessageID import MessageIDFactory
#_ = MessageIDFactory('plinn')
_ = lambda x : lambda : x

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

footer = """
------------
Document : %s
""" % object.absolute_url()


message = context.echange_mail_template(  From = sender
										, To = mto
										, Subject = "=?utf-8?q?%s?=" % encodestring(portal.Title() + " : " + _("Document state change notificaction")()).replace('=\n', '')
										, ContentType = 'text/plain'
										, charset = 'UTF-8'
										, body=sci.kwargs.get('comment', '')
										, footer=footer)


MailHost.send( message.encode('utf-8') )

return recipients
