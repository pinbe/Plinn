##parameters=rootObject=None, filtered_meta_types=['Huge Plinn Folder', 'Portfolio', 'Topic'], userid=''

from Products.CMFCore.utils import getUtilityByInterfaceName

utool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IURLTool')

rootObject = rootObject if rootObject else utool.getPortalObject()

req = context.REQUEST
resp = req.RESPONSE
collapse_all = False
if req.form.get('collapse_all', '') == rootObject.id or req.get('just_login', False):
    collapse_all = True


def getSubObjects(object):
    if getattr(object, 'isPortalContent', False):
        return []
    childs = list(object.listNearestFolderContents(contentFilter={'portal_type': filtered_meta_types}, userid=userid))
    childs.sort(lambda x, y: cmp(x.title_or_id().lower(), y.title_or_id().lower()))
    return childs


from ZTUtils import SimpleTreeMaker

stateName = rootObject.id + userid + '_tree'
cookieName = stateName + '-state'
stm = SimpleTreeMaker(stateName)
stm.setChildAccess(function=getSubObjects)

tree, rows = stm.cookieTree(rootObject)
cookieValue = resp.cookies[cookieName]['value']
resp.setCookie(cookieName, cookieValue, path='/')

return {'tree': tree, 'rows': rows}
