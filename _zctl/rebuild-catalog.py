from argparse import ArgumentParser
import os.path
from Acquisition import aq_base
from zope.site.hooks import setSite
from Products.CMFCore.CMFCatalogAware import CMFCatalogAware
import transaction

count = 0

def checkContents(ob) :
    global count
    try :
        print ob.absolute_url()
    except Exception, e:
        print >> errorLog, '%s/%s' % (ob.aq_parent.absolute_url(), ob.aq_base.id)
        print >> errorLog, getattr(ob, 'portal_type', getattr(ob, 'meta_type', ''))
        print >> errorLog, e
        print >> errorLog
    
    if isinstance(aq_base(ob), CMFCatalogAware) :
        assert ob._getCatalogTool()
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


parser = ArgumentParser(description="Rebuild entire catalog by walking contents tree.")
parser.add_argument('portal_path')
parser.add_argument('--error-log', help='Error log file. Default: ~/catalog-rebuild-error.log',
                    default='~/catalog-rebuild-error.log', required=False, dest='errorLogPath')

args = parser.parse_args()
portal = app.unrestrictedTraverse(args.portal_path)
setSite(portal)
ctool = portal.portal_catalog
errorLogPath = os.path.expanduser(args.errorLogPath)
errorLog = open(errorLogPath, 'w')

try :
    checkContents(portal)
    transaction.commit()
    print count
    print 'Done.'
finally :
    errorLog.close()
    
