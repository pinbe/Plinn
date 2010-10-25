##parameters

if context.REQUEST.form.get('ajax') :
	template = context.main_template_ajax
else :
	template = context.main_template_standard
return template.macros['master']