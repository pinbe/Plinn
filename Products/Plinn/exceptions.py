""" Plinn exceptions



"""
from AccessControl import ModuleSecurityInfo
from DateTime.DateTime import DateTimeError
from Products.CMFCore.WorkflowCore import WorkflowException

security = ModuleSecurityInfo('Products.Plinn.exceptions')
security.declarePublic('DateTimeError')
security.declarePublic('WorkflowException')