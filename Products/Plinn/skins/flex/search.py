##parameters=
from Products.CMFCore.utils import getToolByName
from ZTUtils import make_query as mq
from ZTUtils import make_hidden_input
from Products.Plinn.utils import translate
from Products.Plinn import Batch


def _(message) : return translate(message, context).encode('utf-8')


utool = getToolByName(context, 'portal_url')
portal_url = utool()
ctool = getToolByName(context, 'portal_catalog')
mtool = getToolByName(context, 'portal_membership')
homeDir = mtool.getHomeFolder(verifyPermission=True)
options = {}
indexes = {}
for i in ctool.indexes() :
    indexes[i] = True
hasindex = indexes.has_key

form = context.REQUEST.form
query = {}
skip_vars = ['strCreator', 'ajax', 'b_start']

# list typed criterions
select_vars = ('review_state'
               , 'Subject'
               , 'portal_type'
               )
noFollowVars = []

# first cleaning: remove empty values / dict cast.
for k, v in form.items() :
    if not v : continue
    if k in select_vars :
        if same_type(v, []) :
            v = filter(None, v)
        if not v :
            continue
    if hasattr(v, 'has_key') :
        v = dict(v.items())

    query[k] = v

# simplifications / cleaning again
if query.has_key('portal_type') :
    try :
        query['portal_type'].remove('Member Data')
    except (ValueError, AttributeError) :
        pass
else :
    query['portal_type'] = context.portal_types.objectIds()
    noFollowVars.append('portal_type')

# clean parameters that are not indexes
for k in skip_vars :
    if query.has_key(k) :
        del query[k]

# expand creator search item
if form.has_key('strCreator') and form['strCreator'].strip() :
    query['listCreators'] = [m.getId() for m in context.portal_membership.looseSearchMembers(form['strCreator'])]

# 'mofified' index solving
if query.has_key('modified') :
    def resolveDate(modified) :
        today = context.ZopeTime().earliestTime()
        dateResolution = {'yesterday' : (today - 1).Date()
            , 'lastWeek' : (today - 7).Date()
            , 'lastMonth' : (today - 31).Date()
                          }
        member = mtool.getAuthenticatedMember()
        if member :
            lastLoginTime = member.getProperty('last_login_time', None)
            if lastLoginTime :
                dateResolution['lastLogin'] = lastLoginTime
        return dateResolution.get(modified)


    date = resolveDate(query['modified'])
    if date :
        query['modified'] = {'query' : date, 'range' : 'min'}
    else :
        del query['modified']

sort_on = query.get('sort_on', 'fTitle')
if hasindex(sort_on) :
    query['sort_on'] = sort_on
    query['sort_order'] = query.get('sort_order', 'ascending')
else :
    if query.has_key('sort_on') : query.pop('sort_on')
    if query.has_key('sort_order') : query.pop('sort_order')


def makeColumnHeader(indexName) :
    toggleSortOrder = indexName == sort_on
    columnQuery = query.copy()
    for name in noFollowVars :
        if columnQuery.has_key(name) :
            columnQuery.pop(name)
    columnQuery['sort_on'] = indexName
    sort_order = query.get('sort_order', 'ascending')
    if toggleSortOrder :
        if sort_order == 'ascending' :
            sort_order = 'reverse'
        elif sort_order == 'reverse' :
            sort_order = 'ascending'
    columnQuery['sort_order'] = sort_order
    url = '%s/search?%s' % (portal_url, mq(**columnQuery))

    toggleImg = None
    if toggleSortOrder :  # e.g. selected
        if query['sort_order'] == 'ascending' :
            toggleImg = {'src' : '%s/arrowUp.gif' % portal_url
                , 'alt' : _('ascending sort')}

        elif query['sort_order'] == 'reverse' :
            toggleImg = {'src' : '%s/arrowDown.gif' % portal_url
                , 'alt' : _('ascending sort')}
    return {'url' : url, 'img' : toggleImg}


options['makeColumnHeader'] = makeColumnHeader
results = ctool(**query)
options['resultsLength'] = len(results)

if homeDir and results :
    options['canSaveAsTopic'] = True
    args = query.copy()
    for name in noFollowVars :
        try :
            args.pop(name)
        except :
            pass
    if form.has_key('modified') :
        possibleValues = {'yesterday' : 1
            , 'lastWeek' : 7
            , 'lastMonth' : 31}
        value = possibleValues.get(form['modified'])
        if value :
            d = {'critType' : 'Friendly Date Criterion'
                , 'value' : value
                , 'operation' : 'max'
                , 'daterange' : 'old'}
            args['modified'] = d
        else :
            try :
                del args['modified']
            except KeyError :
                pass
    options['queryAsHiddenInputs'] = make_hidden_input(**args)
else :
    options['canSaveAsTopic'] = False

options['batch'] = Batch(results,
                         context.default_batch_size,
                         form.get('b_start', 0),
                         orphan=1,
                         quantumleap=1)

photo_search_mode = len(query['portal_type']) == 1 and query['portal_type'][0] == 'Photo'

if photo_search_mode :
    options['brains_infos'] = context.getPhotoBrainsInfos(results)
    return context.photo_search_results_template(**options)
else :
    return context.common_search_results_template(**options)
