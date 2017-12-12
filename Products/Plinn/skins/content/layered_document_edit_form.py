##parameters=save_layer='', save_options='', layer=None, edit_type='layer', kopts={}, ajax=''
from Products.CMFCore.utils import getToolByName
from ZTUtils import make_query as mq
from Products.Plinn.utils import Message as _

atool = getToolByName(context, 'portal_attachment')
attachments = atool.getAttachmentsFor(context)

form = context.REQUEST.form
text = form.get('text')

if save_layer and \
        context.edit(form.get('text'), layer) :
    attachments.removeUnusedAttachments(context.layersStack())
    return context.setRedirect(context, 'object/view', **{'ajax' : ajax})

if save_options and \
    context.setKinematicOptions(kopts) :
    return context.setRedirect(context, 'object/view', **{'ajax' : ajax})

options = {}
target = context.getActionInfo('object/edit')['url']
options['form'] = {'action' : target}
options['edit_type'] = edit_type

layers_length = context.getLayerLength()

options['selected_layer'] = layers_length - 1 if layer is None else layer
if edit_type == 'layer' :
    options['selected_tab'] = 'layer_%d' % options['selected_layer']
else :
    options['selected_tab'] = edit_type

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
            {'title' : title,
             'url' : '%s?%s' % (target, mq(edit_type='layer',layer=ln - 1)),
             'id' : 'layer_%d' % (ln - 1)})

options['layerstabs'].append(
        {'title' : _('Kinematic'),
         'url' : '%s?%s' % (target, mq(edit_type='kinematic')),
         'id' : 'kinematic'}
)

return context.layered_document_edit_template(**options)
