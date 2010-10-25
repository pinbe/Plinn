##parameters=
folderishTypes = ['Plinn Folder', 'Calendar', 'Portfolio']
ttool = context.portal_types
allFtis = ttool.listTypeInfo()

ftis = []
for ft in folderishTypes :
	folderishFti = ttool.getTypeInfo(ft)

	for fti in allFtis :
		if folderishFti.allowType(fti.id) and fti not in ftis :
			ftis.append(fti)

ftis.append(ttool['Discussion Item'])
return ftis