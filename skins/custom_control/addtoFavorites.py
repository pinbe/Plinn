## Script (Python) "addtoFavorites"
##title=Add item to favourites
##parameters=ajax=''

#TODO : translate messages
#from Products.PlacelessTranslationService.MessageID import MessageIDFactory
#_ = MessageIDFactory('plinn')
_ = lambda x : lambda : x

portal = context.portal_url.getPortalObject()
ttool = portal.portal_types
homeFolder = portal.portal_membership.getHomeFolder()

if not hasattr(homeFolder, 'Favorites'):
	ttool.constructContent( 'Plinn Folder', homeFolder, 'Favorites', title=str(_('Favorites')) )

targetFolder = getattr( homeFolder, 'Favorites' )
new_id='fav_' + str(int( context.ZopeTime()))
myPath=context.portal_url.getRelativeUrl(context)
targetFolder.invokeFactory( 'Favorite', id=new_id, title=context.TitleOrId(), remote_url=myPath)

context.setStatus(True, 'Favorite added.')
context.setRedirect(context, 'object/view', ajax=ajax)
