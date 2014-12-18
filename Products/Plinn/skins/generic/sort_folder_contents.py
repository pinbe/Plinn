##parameters=objects, sorted_field, sorted_dir

if not objects : return []

mtool = context.portal_membership
wftool = context.portal_workflow

functions = {'title' : lambda ob : ob.title_or_id().lower() ,
			 'date'	 : lambda ob : ob.modified() ,
			 'submitTime' : lambda ob : wftool.getInfoFor(ob, 'time'),
			 'actor' : lambda ob : mtool.getMemberFullNameById(wftool.getInfoFor(ob, 'actor')), 
			 'Creator' : lambda ob : mtool.getMemberFullNameById(ob.Creator()),
			 'review_state' : lambda ob : wftool.getInfoFor(ob, 'review_state', ''),
			 }


sort_func = functions.get(sorted_field, None)
if sort_func is None :
	if hasattr(objects[0], sorted_field):
		sort_func = callable(getattr(objects[0], sorted_field)) and (lambda ob : getattr(ob, sorted_field)()) or (lambda ob : getattr(ob, sorted_field))
	else :
		return objects


objects.sort(sorted_dir == 'down' and (lambda a,b: cmp(sort_func(b), sort_func(a))) or (lambda a,b: cmp(sort_func(a), sort_func(b))))
return objects
