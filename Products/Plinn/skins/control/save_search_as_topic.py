##parameters=
from Products.CMFCore.utils import getToolByName
from Products.Plinn.utils import makeValidId
from Products.Plinn.utils import translate
_ = lambda msg: translate(msg, context)
mtool = getToolByName(context, 'portal_membership')
homedir = mtool.getHomeFolder()

form = context.REQUEST.form.copy()
for k, v in form.items() :
	if hasattr(v, 'has_key') :
		form[k] = dict(v)

title = form.pop('topic_title')
topic_id = makeValidId(homedir, title)
id = homedir.invokeFactory('Topic', topic_id, title=title)
topic = getattr(homedir, id)
topic.loadSearchQuery(form)

context.setStatus(True, _('Topic added.'))
try :
	ajax = form.pop('ajax')
except KeyError :
	ajax = ''
return context.setRedirect(topic, 'object/view', ajax=ajax, syncFragments = ['Breadcrumbs', 'rightCell'])
