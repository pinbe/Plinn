##parameters=success, message='', **kw

if message:
    context.REQUEST.other['portal_status_message'] = message
if kw:
    for k, v in kw.items():
        context.REQUEST.form[k] = v

return success
