##parameters=compare=''

from Products.Plinn.utils import getAdapterByInterface

options = {}
form = context.REQUEST.form
history = getAdapterByInterface(context, 'Products.Plinn.interfaces.IContentHistory', None)
comparison = None
resultsLength = 20
start = form.get('first_transaction', 0)
stop = start + resultsLength
batchNavigation = {}

if history is not None :
    entries = history.listEntries(first=start, last=stop + 1)

    previous, next = None, None
    if len(entries) == resultsLength + 1 :
        entries = entries[0 :-1]
        next = start + resultsLength

    if start > 0 :
        previous = start - resultsLength

    batchNavigation = {'previous' : previous, 'next' : next, 'current' : start}

    options['entries'] = entries
    r = form.get('rightkey', entries[0]['key'])
    try :
        l = form.get('leftkey', entries[1]['key'])
    except IndexError :
        l = r

    options['leftkey'] = l
    options['rightkey'] = r
    if compare :
        comparison = history.compare(l, r)
else :
    options['entries'] = None

options['comparison'] = comparison
options['batchNavigation'] = batchNavigation

return context.changes_history_template(**options)
