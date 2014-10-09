##parameters=change='', change_and_view='', ajax=''
from Products.CMFCore.utils import getToolByName
atool = getToolByName(context, 'portal_attachment')
attachments = atool.getAttachmentsFor(context)

form = context.REQUEST.form
text = form.get('text')
if text and same_type(text, []) :
    # when javascript is disabled,
    # there's a hidden textarea from epoz
    # and an other from <noscript> tag
    form.update({'text' : text[1]}) 

if change_and_view and \
        context.document_edit_control(text=form.get('text'), text_format='html') :
    attachments.removeUnusedAttachments(context.EditableBody())
    return context.setRedirect(context, 'object/view', **{'ajax':ajax})


options = {}

buttons = []
target = context.getActionInfo('object/edit')['url']
buttons.append( {'name': 'change', 'value': 'Change'} )
buttons.append( {'name': 'change_and_view', 'value': 'Change and View'} )
options['form'] = { 'action': target,
                    'listButtonInfos': tuple(buttons) }

return context.document_edit_template(**options)
