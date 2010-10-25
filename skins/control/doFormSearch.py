## Script (Python) "doFormSearch"
##parameters=REQUEST
##title=Pre-process form variables, then return catalog query results.
##
vars = REQUEST.form
form_vars = {}
skip_vars = ['strCreator']
select_vars = ( 'review_state'
			  , 'Subject'
			  , 'portal_type'
			  )
date_vars = ('created',
			 )
epoch = DateTime("1970/01/01 00:00:00 GMT")

for k, v in vars.items():

	if k in select_vars:
		if same_type( v, [] ):
			v = filter( None, v )
		if not v:
			continue

	if k in date_vars:
		if v == epoch and vars.get(k+'_usage') == 'range:min':
			skip_vars.append(k+'_usage')
			continue

	form_vars[ k ] = v

if form_vars.has_key('portal_type') :
	try : form_vars['portal_type'].remove('Member Data')
	except ValueError : pass
else :
	form_vars['portal_type'] = context.portal_types.objectIds()

for k in skip_vars:
	if form_vars.has_key(k) :
		del form_vars[k]

if vars.has_key('strCreator') :
	form_vars['listCreators'] = [ m.getId() for m in context.portal_membership.looseSearchMembers(vars['strCreator']) ]

return context.portal_catalog( form_vars )
