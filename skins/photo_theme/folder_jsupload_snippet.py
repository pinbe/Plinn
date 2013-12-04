##parameters=ob
from Products.CMFCore.utils import getUtilityByInterfaceName
utool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IURLTool')
locale_date_fmt = context.locale_date_fmt()
infos = {'checkbox' : True,
         'url' : ob.absolute_url(),
         'lock' : False,
         'modified' : ob.modified().strftime(locale_date_fmt),
         'title_or_id' : ob.title_or_id(),
         'position' : context.getObjectPosition(ob.getId()),
         'type' : ob.Type() or None,
         'id' : ob.getId(),
         'icon': '%s/%s' % (utool(), ob.getIcon())}

return context.folder_jsupload_snippet_template(listItemInfos=[infos])