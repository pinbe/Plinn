##parameters=rows, position
if position is None :
	return None
else :
	reply = context.talkback.getReply(position)
	
	def isChildOfReply(firstAprox, reply) :
		thread = reply.parentsInThread() + reply.getReplies() # hum !
		return firstAprox in thread
	
	for i in range(len(rows)) :
		if rows[i].object == reply :
			break

	while rows[i].state > 0 and isChildOfReply(reply, rows[i].object) :
		i+=1

	return rows[i].object.id