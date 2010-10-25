## Script (Python) "undo"
##title=Undo transactions
##parameters=transaction_info, ajax=''
context.portal_undo.undo(context, transaction_info)

return context.REQUEST.RESPONSE.redirect(
    'undo_form?portal_status_message=Transaction(s)+undone&ajax=%s' % ajax )
