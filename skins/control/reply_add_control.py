##parameters=title, text, **kw
title = title.strip()
text = text.strip()

if title and text :
	try : talkback = context.talkback
	except : talkback = context.portal_discussion.getDiscussionFor(context)
	replyId = talkback.createReply(title=title, text=text)
	return context.setStatus(replyId, 'Comment added.')
else :
	return context.setStatus(False, 'You must enter a title and body.')