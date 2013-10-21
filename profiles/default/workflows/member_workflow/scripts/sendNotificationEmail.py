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
#cmfMessages = MessageIDFactory('cmf_default')
_ = cmfMessages = lambda x : lambda : x
from quopri import encodestring

portal = context.portal_url.getPortalObject()
mtool = portal.portal_membership
rtool = portal.portal_registration
MailHost = portal.MailHost


def encodeAdr(member) :
	name = member.getMemberFullName(nameBefore=0)
	email = member.getProperty('email')
	qpName = encodestring(name).replace('=\n', '')
	return '''"=?utf-8?q?%s?=" <%s>''' % (qpName, email)

member = sci.object

sender = mtool.getAuthenticatedMember()
sender = encodeAdr(sender)
mto = encodeAdr(member)

text = _( """
You have been registered as a member of "%(portal_title)s", which
allows you to personalize your view of the website and participate in
the community.
""".strip().replace('\n', ' ') )() % {'portal_title' :portal.Title()}

if portal.getProperty('validate_email') :
	text += '\n'
	text += _( """You will receive an other mail with your randomly-generated
password. Once you have logged in with this password, you
may change it to anything you like.""".strip().replace('\n', ' ') )()

else :
	text += '\n'*2
	text += cmfMessages( "You can use this URL to log in:" )()
	text += '\n' + portal.absolute_url() + '/login_form'

message = context.echange_mail_template(  From = sender
										, To = mto
										, Subject = "=?utf-8?q?%s?=" % encodestring(portal.Title() + " : " + \
										_("your registration has been accepted")()).replace('=\n', '')
										, ContentType = 'text/plain'
										, charset = 'UTF-8'
										, body= text
										)


MailHost.send( message )
if portal.getProperty('validate_email') :
	rtool.mailPassword(member.getId(), context.REQUEST)
