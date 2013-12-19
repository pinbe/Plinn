from Products.Plinn.HugePlinnFolder import HugePlinnFolder

IGNORED_ATTRIBUTES = ('_objects',)

def migrateFolder(old, container) :
    print 'migrate %s' % old.absolute_url()

    origid = old.getId()
    title = old.Title()
    toBeSkipped = IGNORED_ATTRIBUTES + tuple(old.objectIds())

    new = HugePlinnFolder(origid, title=title)

    for name in old.__dict__.keys() :
        if name in toBeSkipped :
            continue
        else :
            setattr(new, name, getattr(old, name))
        
    new._populateFromFolder(old)

    container._delOb(origid)
    container._setOb(origid, new)

    return container._getOb(origid)
