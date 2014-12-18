##parameters=
items = context.getCriteriaItems()
if items :
	from Products.Plinn.utils import translate
	_ = lambda msg: translate(msg, context)

	rec = items[0][1]
	
	query = rec['query']
	range = rec['range']
	
	strftime = lambda d : d.strftime(context.locale_date_fmt())
	
	if range == 'max' :
		return _("search from the beginning of the world until %s") % strftime(query)
	elif range == 'min' :
		return _("search from %s and the end of the world") % strftime(query)
	elif range == 'min:max' :
		return _("search between %s and %s") % (strftime(query[0]), strftime(query[1]))
else :
	return context.Description()