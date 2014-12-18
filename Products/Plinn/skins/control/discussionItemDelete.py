## Script (Python) "discussionItemDelete"
##title=Add item to favourites
##parameters=
from Products.CMFCore.utils import getToolByName
disTool = getToolByName(context, 'portal_discussion')
thread = context.parentsInThread()
content = thread[0]
talk = disTool.getDiscussionFor(context)

if talk.hasReplies(context) :
	context.setStatus(True, 'Discussion thread deleted.')
else :
	if len(thread) == 1:
		context.setStatus(True, 'Comment deleted.')
	else :
		context.setStatus(True, 'Reply deleted.')


talk.deleteReply(context.id)

return context.setRedirect(content, 'object/view', **context.REQUEST.form)
