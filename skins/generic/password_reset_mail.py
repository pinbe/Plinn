##parameters=options={}
from Products.Plinn.utils import translate as _

print _('Hi %(fullName)s,')
print
print _('You recently asked to reset your password.')

print _("To get back into your account on the %(siteName)s website, you'll need to create a new password.")
print _("It's easy:")
print '— %s' % _("Click the link below to open a browser window.")
print '— %s' % _("Fill the form with your new password.")
print
print '%(resetPasswordUrl)s'

return printed % options