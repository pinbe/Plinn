##parameters=
form = context.REQUEST.form
form_has = form.has_key

if context.meta_type == 'Discussion Item' :
	contentOb = context.parentsInThread()[0]
else :
	contentOb = context

if form_has('cancel_reply') :
	contentOb.setRedirect(contentOb, 'object/view', **form)
	return
elif form_has('add_reply') :
	replyId = context.reply_add_control(**form)
	if replyId :
		context.setRedirect(contentOb, 'object/view', new_reply_id=replyId, **form)
		return

options = {'reply_for_ob' : context, 'ajax' : form_has('ajax') and '1' or None, 'inReplyTo' : context}
return getattr(contentOb, contentOb.getActionInfo('object/view')['url'].split('/')[-1])(**options)