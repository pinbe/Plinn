##parameters=*arg, **kw
reqOther = context.REQUEST.other
if hasattr(context, 'index_html') :
	homePath = context.index_html.getPhysicalPath()
	folderPath = context.getPhysicalPath()
	if len(homePath) == len(folderPath) + 1 and homePath[:-1] == folderPath:
		reqOther['forceTab'] = 'view'
		return context.index_html(*arg, **kw)

reqOther['forceTab'] = 'folderContents'
return context.folder_contents(*arg, **kw)