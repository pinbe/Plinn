##parameters=items, **kw
##title=Rename objects in a folder
##
from Products.CMFDefault.exceptions import CopyError
from Products.Plinn.utils import translate
_ = lambda msg : translate(msg, context)

ids, new_ids = zip(*[(i['id'], i['new_id']) for i in items])
changed = 0

c = context.aq_explicit
for itemInfo in items :
    item = getattr(c, itemInfo['id'])
    if item.Title() != itemInfo['title'] :
        item.setTitle(itemInfo['title'])
        item.reindexObject()
        changed = changed + 1

if not ids == new_ids:
    try:
        skiped = context.manage_renameObjects(ids, new_ids)
        if not skiped :
            if len(ids) == 1:
                return context.setStatus(True, _(u'Item renamed.'))
            else:
                return context.setStatus(True, _(u'Items renamed.'))
        else :
            if len(skiped) == 1 :
                return context.setStatus(True, _( u'This item has not been renamed: "%s"') % ids[0] )
            else :
                return context.setStatus(True
                                        , _( u'These items have not been renamed: %s') % \
                                            ', '.join(['"%s"' % id for id in ids]) )
    except CopyError:
        return context.setStatus(False, _(u'Rename failed.'))


elif not changed :
  return context.setStatus(False, _(u'Nothing to change.'))
else :
    if changed == 1:
        return context.setStatus(True, _(u'Item renamed.'))
    else:
        return context.setStatus(True, _(u'Items renamed.'))
    