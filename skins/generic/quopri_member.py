##parameters=member=None, name='', email=''
from quopri import encodestring
if member is not None :
	n = member.getMemberFullName(nameBefore=0)
	e = member.getProperty('email')
else :
	n = name
	e = email
	
qpName = encodestring(n).replace('=\n', '')
return '''"=?utf-8?q?%s?=" <%s>''' % (qpName, e)
