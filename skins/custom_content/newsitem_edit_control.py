##parameters=text, text_format, SafetyBelt='', **kw
##
from Products.CMFDefault.exceptions import EditingConflict
from Products.CMFDefault.exceptions import ResourceLockedError

if text_format != context.text_format or text != context.text:
    try:
        context.edit(text, text_format = text_format)#, safety_belt=SafetyBelt)
        return context.setStatus(True, 'Document changed.')
    except (ResourceLockedError, EditingConflict), errmsg:
        return context.setStatus(False, errmsg)
else:
    return context.setStatus(False, 'Nothing to change.')
