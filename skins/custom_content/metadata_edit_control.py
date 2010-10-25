##parameters=allow_discussion=None, title=None, subject=None, description=None, contributors=None, effective_date=None, expiration_date=None, format=None, language=None, rights=None, ajax='', **kw
##
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.exceptions import ResourceLockedError

dtool = getToolByName(script, 'portal_discussion')

def tuplify( value ):

	if not same_type( value, () ):
		value = tuple( value )

	temp = filter( None, value )
	return tuple( temp )

if title is None:
	title = context.Title()

if subject is None:
	subject = context.Subject()
else:
	subject = tuplify( subject )

if description is None:
	description = context.Description()

if contributors is None:
	contributors = context.Contributors()
else:
	contributors = tuplify( contributors )

if effective_date is None:
	effective_date = context.effective()
else :
	if dict(effective_date) == {'year':'1969', 'month':'12', 'day':'31', 'hour':'00', 'minute':'00'} :
		effective_date = None
	else :
		effective_date = '%(year)s/%(month)s/%(day)s %(hour)s:%(minute)s' % effective_date

if expiration_date is None:
	expiration_date = context.expires()
else :
	expiration_date = '%(year)s/%(month)s/%(day)s %(hour)s:%(minute)s' % expiration_date


if format is None:
	format = context.Format()

if language is None:
	language = context.Language()

if rights is None:
	rights = context.Rights()

if allow_discussion is not None :
	if allow_discussion == 'default':
		allow_discussion = None
	if allow_discussion == 'off':
		allow_discussion = False
	elif allow_discussion == 'on':
		allow_discussion = True
	dtool.overrideDiscussionFor(context, allow_discussion)

try:
	context.editMetadata( title=title
						, description=description
						, subject=subject
						, contributors=contributors
						, effective_date=effective_date
						, expiration_date=expiration_date
						, format=format
						, language=language
						, rights=rights
						)
	if ajax : return '...'
	context.setStatus(True, 'Metadata changed.')
	return context.setRedirect(context, 'object/edit')
except ResourceLockedError, errmsg:
	return False
