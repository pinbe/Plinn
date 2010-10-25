""" Plinn exceptions

$Id: exceptions.py 1261 2008-01-07 01:34:23Z pin $
$URL: http://svn.cri.ensmp.fr/svn/Plinn/branches/CMF-2.1/exceptions.py $
"""
from AccessControl import ModuleSecurityInfo
from DateTime.DateTime import DateTimeError
from Products.CMFCore.WorkflowCore import WorkflowException

security = ModuleSecurityInfo('Products.Plinn.exceptions')
security.declarePublic('DateTimeError')
security.declarePublic('WorkflowException')