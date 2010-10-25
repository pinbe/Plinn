##parameters=title='', description='', event_type=[], start_date={}, end_date={}, location='', contact_name='', contact_email='', contact_phone='', event_url='', **kw
##
from Products.CMFCalendar.exceptions import ResourceLockedError
from Products.Plinn.exceptions import DateTimeError
from DateTime import DateTime

try :
	startDate = DateTime('%s/%s/%s %s %s' % (start_date['year'],
											 start_date['month'],
											 start_date['day'],
											 start_date['hour'],
											 start_date['minute']) )
	context.setStartDate(startDate)
except DateTimeError:
	return context.setStatus(False, "Start date is not valid.")


try :
	endDate = DateTime('%s/%s/%s %s %s' % (end_date['year'],
										   end_date['month'],
										   end_date['day'],
										   end_date['hour'],
										   end_date['minute']) )
	context.setEndDate(endDate)
except DateTimeError:
	return context.setStatus(False, "End date is not valid.")

try:
	context.edit( title=title
				, description	= description
				, location		= location
				, contact_name	= contact_name
				, contact_email	= contact_email
				, contact_phone	= contact_phone
				, event_url		= event_url
				, eventType		= event_type
				
				, effectiveDay	= startDate.day()
				, effectiveMo	= startDate.month()
				, effectiveYear	= startDate.year()
				, start_time	= startDate.AMPM()
				, startAMPM=''

				, expirationDay		= endDate.day()
				, expirationMo		= endDate.month()
				, expirationYear	= endDate.year()
				, stop_time			= endDate.AMPM()
				, stopAMPM=''

				)
	return context.setStatus(True, 'Event changed.')
except ResourceLockedError, errmsg:
	return context.setStatus(False, errmsg)
