## Script (Python) "setup_talkback_tree"
##parameters=tree_root, force_expand=None
##title=Standard Tree
##
from ZTUtils import SimpleTreeMaker

tm = SimpleTreeMaker('tb_tree')
def getKids(object):
	return object.talkback.getReplies()
tm.setChildAccess(function=getKids)

newReplyId = context.REQUEST.form.get('new_reply_id', None)
if newReplyId :
	reply = tree_root.talkback.getReply(newReplyId)
	parents = {}
	for p in reply.parentsInThread() : parents[p.id] = True
	onBranch = parents.has_key
	tm.setStateFunction( lambda o, s : onBranch(o.id) and 1 or s )
	
elif force_expand :
	reply = tree_root.talkback.getReply(force_expand)
	parents = {}
	for p in reply.parentsInThread() : parents[p.id] = True
	onBranch = parents.has_key
	tm.setStateFunction( lambda o, s : onBranch(o.id) and 2 or s )

tree, rows = tm.cookieTree(tree_root)

resp = context.REQUEST.RESPONSE
cookieValue = resp.cookies['tb_tree-state']['value']
resp.setCookie('tb_tree-state', cookieValue, path = '/')


rows.pop(0)
return {'root': tree, 'rows': rows}
