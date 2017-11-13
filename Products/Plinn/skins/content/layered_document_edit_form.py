##parameters=save='', layer=0, ajax=''
from Products.CMFCore.utils import getToolByName
atool = getToolByName(context, 'portal_attachment')
attachments = atool.getAttachmentsFor(context)

form = context.REQUEST.form
text = form.get('text')

if save and \
        context.edit(form.get('text'), layer) :
    attachments.removeUnusedAttachments(context.getLayer(layer))
    return context.setRedirect(context, 'object/view', **{'ajax':ajax})


options = {}
target = context.getActionInfo('object/edit')['url']
options['form'] = {'action': target}

return context.layered_document_edit_template(**options)
