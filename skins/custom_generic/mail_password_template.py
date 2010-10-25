##parameters=rtool, request, member=None, password=''

#TODO : translate messages
#from Products.PlacelessTranslationService.MessageID import MessageIDFactory
#_ = MessageIDFactory('cmf_default')
_ = lambda x : lambda : x
from quopri import encodestring

portal = context.portal_url.getPortalObject()
mtool = portal.portal_membership


def convertMessage(msg) :
	return msg.replace('${', '%(').replace('}', ')s')

def encodeAdr(member) :
	name = member.getMemberFullName(nameBefore=0)
	email = member.getProperty('email')
	qpName = encodestring(name).replace('=\n', '')
	return '''"=?utf-8?q?%s?=" <%s>''' % (qpName, email)

mfromName   = portal.email_from_name
mfromEmail  = portal.email_from_address
mfromQpName = encodestring(mfromName).replace('=\n', '')
mfrom       = '''"=?utf-8?q?%s?=" <%s>''' % (mfromQpName, mfromEmail)

sender = mfrom
mto = encodeAdr(member)

subject = convertMessage(_("${portal_title}: Membership reminder")()) % {'portal_title': portal.title}

text = []
pr = text.append

pr(convertMessage(_("Your member id and password are: Member ID: ${member_id} Password: ${password}")()) % {'member_id':member.getId(), 'password':password})
pr('')
pr(_("You can use this URL to log in:")())
pr('')

login_url = mtool.getActionInfo('user/login')['url']
pr(login_url)
pr('')

if len(login_url) > 70 :
	pr(_("Be aware that this URL might wrap over two lines. If your browser shows an error message when you try to access the URL please make sure that you put in the complete string.")())


time = context.ZopeTime().strftime(_("%Y/%m/%d at %I:%M:%S %p")())
ip = request.HTTP_X_FORWARDED_FOR or request.REMOTE_ADDR
pr(convertMessage(_("Request made by IP ${ip} at ${time}")()) % {'ip':ip, 'time':time})
	
text = '\n'.join(text)

message = context.echange_mail_template(  From = sender
										, To = mto
										, Subject = "=?utf-8?q?%s?=" % encodestring(subject).replace('=\n', '')
										, ContentType = 'text/plain'
										, charset = 'UTF-8'
										, body= text
										)
return message.encode('utf-8')