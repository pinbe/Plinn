##parameters=save='', layer=None, ajax=''
from Products.CMFCore.utils import getToolByName
from ZTUtils import make_query as mq
from Products.Plinn.utils import Message as _

atool = getToolByName(context, 'portal_attachment')
attachments = atool.getAttachmentsFor(context)

form = context.REQUEST.form
text = form.get('text')

if save and \
        context.edit(form.get('text'), layer) :
    attachments.removeUnusedAttachments(context.layersStack())
    return context.setRedirect(context, 'object/view', **{'ajax' : ajax})

options = {}
target = context.getActionInfo('object/edit')['url']
options['form'] = {'action' : target}

layers_length = context.getLayerLength()

options['selected_layer'] = layers_length - 1 if layer is None else layer
options['selected_tab'] = 'layer_%d' % options['selected_layer']
options['layer_html'] = context.getLayer(options['selected_layer'])

options['layerstabs'] = []
for ln in range(layers_length, 0, -1) :
    if ln == layers_length :
        title = _('Foreground')
    elif ln == 1 :
        title = _('Background')
    else :
        title = _('Layer ${n}', mapping={'n' : ln})

    options['layerstabs'].append(
            {'available' : True,
             'category' : 'object',
             'description' : '',
             'icon' : '',
             'title' : title,
             'url' : '%s?%s' % (target, mq(layer=ln-1)),
             'visible' : True,
             'allowed' : True,
             'link_target' : None,
             'id' : 'layer_%d' % (ln - 1)})

return context.layered_document_edit_template(**options)
