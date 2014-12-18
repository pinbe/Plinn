## Script (Python) "topic_addCriterion"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=field, criterion_type, **kw
##title=
##

try :
	context.addCriterion(field=field, criterion_type=criterion_type)
	return context.setStatus(True, 'Criterion added.')
except :
	return context.setStatus(False, 'Criterion adding canceled.')