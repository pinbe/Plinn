##parameters=options={}
from Products.Plinn.utils import translate as _


print _('Hi %(fullName)s,')
print
if not options.get('initial') :
    print _('You recently asked to reset your password.')

    print _("To get back into your account on the %(siteName)s website, you'll need to create a new password.")
    print _("It's easy:")
    print '— %s' % _("Click the link below to open a browser window.")
    print '— %s' % _("Fill the form with your new password.")
    print
else :
    print _('You just sign up on the %(siteName)s website.')
    print _('Now you have to create your password to complete your registration.')
    print _("It's easy:")
    print '— %s' % _("Click the link below to open a browser window.")
    print '— %s' % _("Choose a password and enter it in the form.")
print '%(resetPasswordUrl)s'

if options['loginIsNotEmail'] :
    print
    print _("Please note:")
    print _("Your personal login to sign in later is:")
    print "%(member_id)s"

return printed % options