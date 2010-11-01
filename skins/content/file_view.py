##parameters=

options = {}

if context.content_type == 'application/x-shockwave-flash' :
	options['width'] = context.getProperty('width', 600)
	options['height'] = context.getProperty('height', 600)
	return context.flash_view_template(**options)

return context.file_view_template(**options)
