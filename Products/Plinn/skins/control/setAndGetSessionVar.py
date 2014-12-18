##parameters=key, value, allowFalse = 1
sd = context.session_data_manager.getSessionData(create = 1)
if allowFalse :
	sd[key] = value
	return value
else :
	if value :
		sd[key] = value
	return sd.get(key, None)