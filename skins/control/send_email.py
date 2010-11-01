##parameters= other_adr=[], batchM=[], customized_batch={}, expand='', collapse='', subject='', text_body='', wfid=None, send_fields={}, ajax=''
recipients = {'to':[], 'cc':[], 'bcc':[]}
if expand or collapse :
	if expand :
		expand = expand.keys()[0]
	return context.send_email_form(other_adr=other_adr, expand=expand,
								   batchM=batchM, customized_batch=customized_batch,
								   subject=subject, text_body=text_body,
								   send_fields=send_fields)
if batchM :
	rolesAndMembers = dict(context.getRecipients())
	for role in batchM :
		field = send_fields[role]
		recipients[field].extend( [m.id for m in rolesAndMembers[role]] )

for role, b in customized_batch.items() :
	field = send_fields[role]
	recipients[field].extend( b )


other_adr = filter(None, other_adr)
if not (reduce(lambda a, b : a+b, recipients.values()) or other_adr)  :
	context.setStatus(False, 'No email sent : no recipient specified.')
	return context.setRedirect(context, 'object/view')

portal = context.portal_url.getPortalObject()
mtool = portal.portal_membership
MailHost = portal.MailHost

from quopri import encodestring

def encodeAdr(member) :
	name = member.getMemberFullName(nameBefore=0)
	email = member.getProperty('email')
	qpName = encodestring(name).replace('=\n', '')
	return '''"=?utf-8?q?%s?=" <%s>''' % (qpName, email)

sender = mtool.getAuthenticatedMember()
sender = encodeAdr(sender)


recipientsFormated = {'to':'', 'cc':'', 'bcc':''}
for field, b in recipients.items() :
	formated = map(encodeAdr, mtool.getMembers(b))
	formated = filter(None, formated)
	formated = ', '.join(formated)
	recipientsFormated[field] = formated

if other_adr :
	recipients['to'].extend(other_adr)
	formated = ', '.join(other_adr)
	to = ', '.join([recipientsFormated['to'], formated])
	to = to.strip(', ')
	recipientsFormated['to'] = to
	
recipientsHeader = []
for field in ['to', 'cc', 'bcc'] :
	value = recipientsFormated[field]
	if value :
		recipientsHeader.append('%s: %s' % (field.capitalize(), value))

recipientsHeader = '\n'.join(recipientsHeader)	

message = context.echange_mail_template(  From = sender
										, recipients = recipientsHeader
										, Subject = "=?utf-8?q?%s?=" % encodestring(subject).replace('=\n', '')
										, ContentType = 'text/plain'
										, charset = 'UTF-8'
										, body=text_body)

MailHost.send( message.encode('utf-8') )

if wfid is not None :
	wtool = portal.portal_workflow
	email_sent = reduce(lambda a, b : a+b, recipients.values())
	wtool.doActionFor(context, 'send_email', wf_id=wfid,
					  email_sent=email_sent,
					  comment=text_body)

context.setStatus(True, 'Email sent.')
return context.setRedirect(context, 'object/view', ajax=ajax)