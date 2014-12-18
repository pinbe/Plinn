from argparse import ArgumentParser
import os.path
from Acquisition import aq_base
from zope.site.hooks import setSite
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
import transaction

count = 0
errorLog = None

def checkContents(ob) :
    global count
    global errorLog
    try :
        print ob.absolute_url()
    except Exception, e:
        print >> errorLog, '%s/%s' % (ob.aq_parent.absolute_url(), ob.aq_base.id)
        print >> errorLog, getattr(ob, 'portal_type', getattr(ob, 'meta_type', ''))
        print >> errorLog, e
        print >> errorLog
    
    if isinstance(aq_base(ob), CMFCatalogAware) :
        ctool = ob._getCatalogTool()
        assert ctool
        try :
            ctool.indexObject(ob)
            count = count + 1
            if count % 1000 == 0 :
                transaction.commit()
                print count, 'commit.'
        except Exception, e:
            print >> errorLog, '%s/%s' % (ob.aq_parent.absolute_url(), ob.aq_base.id)
            print >> errorLog, e
        
    if hasattr(aq_base(ob), 'objectItems') :
        obs = ob.objectItems()
        for k, v in obs :
            checkContents(v)


def indexMemberdata(portal) :
    mtool = portal.portal_membership
    ctool = portal.portal_catalog
    for m in mtool.getOtherMembers([]) :
        ctool.indexObject(m)

def main(path) :
    portal = app.unrestrictedTraverse(path)
    setSite(portal)
    errorLogPath = os.path.expanduser(args.errorLogPath)
    global errorLog
    errorLog = open(errorLogPath, 'w')

    try :
        checkContents(portal)
        transaction.commit()
        indexMemberdata(portal)
        transaction.commit()
        print count
        print 'Done.'
    finally :
        errorLog.close()
    


if __name__ == '__main__':
    parser = ArgumentParser(description="Rebuild entire catalog by walking contents tree.")
    parser.add_argument('portal_path')
    parser.add_argument('--error-log', help='Error log file. Default: ~/catalog-rebuild-error.log',
                        default='~/catalog-rebuild-error.log', required=False, dest='errorLogPath')

    args = parser.parse_args()
    main(args.portal_path)
    
