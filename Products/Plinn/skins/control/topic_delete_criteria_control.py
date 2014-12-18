##parameters=criterion_ids=[], **kw

if criterion_ids :
	for cid in criterion_ids :
		context.deleteCriterion(cid)
	if len(criterion_ids) > 1 :
		return context.setStatus(True, 'Criteria deleted.')
	else :
		return context.setStatus(True, 'Criterion deleted.')
else :
	return context.setStatus(False, 'Please select one ore more criteria first.')
