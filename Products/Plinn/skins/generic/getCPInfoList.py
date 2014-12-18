##parameters=

cp = context.getCPInfo()
objectInfos = []
rt = context.restrictedTraverse
if cp is not None :
	for path in cp[1] :
		ob = rt(path, None)
		icon = rt(ob.getIcon())
		if ob :
			objectInfos.append({'title'		: ob.title_or_id(),
								'url'		: ob.absolute_url(),
								'icon'		: icon.absolute_url(),
								'height'	: icon.height,
								'width'		: icon.width,
								'type'		: ob.getPortalTypeName()
								}
							)
return objectInfos