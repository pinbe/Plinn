##parameters=ajax=''
parent = context.aq_parent
parent.manage_delObjects(context.id)

context.getOrSetSessionVar('slink_mode', 'view')
context.setStatus(True, 'Object deleted.')
return context.setRedirect(parent, 'object/view', ajax=ajax)