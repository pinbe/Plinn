##parameters=

from Products.Plinn.utils import getLdJson
context.REQUEST.RESPONSE.setHeader('Content-Type', 'text/plain;charset=utf-8')
return getLdJson(context, indent=2)