##parameters=key, value=None, default=None
sd = context.session_data_manager.getSessionData(create = 1)
if value is None :
	sVar = sd.get(key, None)
	if sVar is None and default is not None :
		sVar = default
else :
	sVar = value

sd[key] = sVar
return sVar
