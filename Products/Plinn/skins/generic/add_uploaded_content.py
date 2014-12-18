##parameters=
#assumes that jupload send files one by one.
from Products.CMFCore.exceptions import BadRequest
from Products.CMFCore.utils import getToolByName
from Products.Plinn.utils import makeValidId
form = context.REQUEST.form
ctr = getToolByName(context, 'content_type_registry')

file = [form[name] for name in form.keys() if name.startswith('File')][0]
filename = file.filename
utf8filename = filename.split('%25')[0]
if utf8filename != filename :
	for p in filename.split('%25')[1:] :
		utf8filename += chr(int(p[0:2], 16)) + p[2:]
	filename = utf8filename

allow_dup = form.get('overwrite', False)
id = makeValidId(context, filename, allow_dup=allow_dup)
mt = form['mimetype[]']

# adapted from plone jupload
pt = ctr.findTypeName(id.lower(), mt, file)
try:
	id = context.invokeFactory(	type_name=pt,
							id=id,
							file='',
							content_type=mt)
	o = getattr(context, id)
	o.manage_upload(file)
except BadRequest:
	if allow_dup :
		o = getattr(context, id)
		if o.meta_type == 'Photo' :
			o.manage_upload(file)
		else :
			o.edit(file=file)
	else :
		raise
except TypeError:
	# looks like the constructor does no support a file argument
	# (probably trying to create a cmf document)
	context.invokeFactory(	type_name=pt,
							id=id,
							text_format=mt.split('/')[1],
							text=file.read())

return 'SUCCESS'
