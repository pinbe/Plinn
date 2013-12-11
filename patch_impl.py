from ZTUtils import make_query
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.exceptions import zExceptions_Unauthorized
from Products.CMFDefault.utils import translate

def _setRedirect(self, provider_id, action_path, keys=''):
    # Products.CMFDefault.formlib.form._EditFormMixin._setRedirect Plinn implementation
    provider = getToolByName(self.context, provider_id)
    try:
        target = provider.getActionInfo(action_path, self.context,
                                        check_condition=1)['url']
    except (ValueError, zExceptions_Unauthorized):
        target = self._getPortalURL()

    kw = {}
    if self.status:
        message = translate(self.status, self.context)
        if isinstance(message, unicode):
            message = message.encode(self._getBrowserCharset())
        kw['portal_status_message'] = message
    for k in keys.split(','):
        k = k.strip()
        v = self.request.form.get(k, None)
        if v:
            kw[k] = v

    if self.request.form.has_key('ajax') :
        kw['ajax'] = self.request.form['ajax']
    query = kw and ('?%s' % make_query(kw)) or ''
    self.request.RESPONSE.redirect('%s%s' % (target, query))

    return ''
