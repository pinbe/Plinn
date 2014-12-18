##parameters=
form = context.REQUEST.form.copy()
form.pop('ajax', None)
pathAndpropName, value = form.popitem()
path, propName = pathAndpropName.split('//')
ob = context.restrictedTraverse(path)
ob.editMetadata(**{propName:value})
return getattr(ob, propName)